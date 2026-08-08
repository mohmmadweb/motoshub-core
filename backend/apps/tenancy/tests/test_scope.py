"""Organisational scope: who reaches what, and who cannot.

The interface has its own copy of this model for deciding what to render, but
rendering is a courtesy. These tests are about the server refusing to hand over
another subsidiary's content, however the request is shaped.
"""
import pytest
from django.test import Client

from apps.content.models import News
from apps.rbac.models import Role, RoleAssignment
from apps.tenancy.models import Company, CompanyMembership, Holding
from apps.tenancy.scope import COMPANY, HOLDING, SYSTEM, scope_for


@pytest.fixture
def org(tenant):
    """Two holdings, two companies each — enough for scope to be meaningful."""
    alpha = Holding.objects.create(tenant=tenant, name="هلدینگ الف", color="#111111")
    beta = Holding.objects.create(tenant=tenant, name="هلدینگ ب", color="#222222")
    return {
        "alpha": alpha,
        "beta": beta,
        "a1": Company.objects.create(tenant=tenant, holding=alpha, name="شرکت الف-۱"),
        "a2": Company.objects.create(tenant=tenant, holding=alpha, name="شرکت الف-۲"),
        "b1": Company.objects.create(tenant=tenant, holding=beta, name="شرکت ب-۱"),
    }


@pytest.fixture
def news(tenant, admin, org):
    """One item at each scope, so leaks are visible by title."""
    mk = lambda **kw: News.objects.create(tenant=tenant, author=admin, visibility="public", **kw)
    return {
        "global": mk(title="خبر سراسری", scope="global"),
        "alpha": mk(title="خبر هلدینگ الف", scope="holding", holding=org["alpha"]),
        "beta": mk(title="خبر هلدینگ ب", scope="holding", holding=org["beta"]),
        "a1": mk(title="خبر شرکت الف-۱", scope="company", holding=org["alpha"], company=org["a1"]),
        "b1": mk(title="خبر شرکت ب-۱", scope="company", holding=org["beta"], company=org["b1"]),
    }


def _titles(response) -> set[str]:
    return {row["title"] for row in response.json()["data"]}


def _member_of(user, company, tenant):
    CompanyMembership.objects.create(user=user, company=company)
    RoleAssignment.objects.filter(user=user).delete()
    RoleAssignment.objects.create(
        user=user, role=Role.objects.get(key="member"), tenant=tenant, company=company,
    )


# ── resolution ───────────────────────────────────────────────────────────────
@pytest.mark.django_db
def test_a_company_member_is_scoped_to_their_company(member, tenant, org):
    _member_of(member, org["a1"], tenant)
    s = scope_for(member, tenant)
    assert s.level == COMPANY
    assert str(org["a1"].id) in {str(x) for x in s.company_ids}
    assert s.publishable == ["شرکت"]


@pytest.mark.django_db
def test_membership_of_several_companies_widens_reach(member, tenant, org):
    _member_of(member, org["a1"], tenant)
    CompanyMembership.objects.create(user=member, company=org["b1"])
    s = scope_for(member, tenant)
    assert {str(x) for x in s.company_ids} >= {str(org["a1"].id), str(org["b1"].id)}
    # Two holdings reached, so the switcher becomes meaningful.
    assert s.can_switch([org["alpha"], org["beta"]], [org["a1"], org["a2"], org["b1"]])


@pytest.mark.django_db
def test_a_holding_role_covers_its_companies(member, tenant, org):
    RoleAssignment.objects.filter(user=member).delete()
    RoleAssignment.objects.create(
        user=member, role=Role.objects.get(key="org-admin"), tenant=tenant, holding=org["alpha"],
    )
    s = scope_for(member, tenant)
    assert s.level == HOLDING
    assert s.publishable == ["هلدینگ", "شرکت"]


@pytest.mark.django_db
def test_platform_admin_is_system_level(platform_admin, tenant):
    s = scope_for(platform_admin, tenant)
    assert s.level == SYSTEM
    assert s.publishable == ["سراسری", "هلدینگ", "شرکت"]


# ── enforcement ──────────────────────────────────────────────────────────────
@pytest.mark.django_db
def test_a_company_member_never_sees_another_subsidiary(member, tenant, auth, org, news):
    _member_of(member, org["a1"], tenant)
    seen = _titles(Client().get("/api/v1/news", **auth(member, tenant)))

    assert "خبر سراسری" in seen, "global content reaches everyone"
    assert "خبر شرکت الف-۱" in seen, "their own company's content reaches them"
    assert "خبر هلدینگ الف" in seen, "their holding's content reaches them"
    assert "خبر شرکت ب-۱" not in seen, "another subsidiary must not leak"
    assert "خبر هلدینگ ب" not in seen, "another holding must not leak"


@pytest.mark.django_db
def test_system_level_sees_everything(platform_admin, tenant, auth, news):
    seen = _titles(Client().get("/api/v1/news", **auth(platform_admin, tenant)))
    assert seen >= {"خبر سراسری", "خبر هلدینگ الف", "خبر هلدینگ ب", "خبر شرکت الف-۱", "خبر شرکت ب-۱"}


@pytest.mark.django_db
def test_the_switcher_can_narrow_but_never_widen(member, tenant, auth, org, news):
    """Pointing at a domain you do not belong to must not reveal it."""
    _member_of(member, org["a1"], tenant)
    headers = {**auth(member, tenant), "HTTP_X_SCOPE_COMPANY": str(org["b1"].id)}
    seen = _titles(Client().get("/api/v1/news", **headers))
    assert "خبر شرکت ب-۱" not in seen
    # The forged header is ignored, so their own reach still applies.
    assert "خبر سراسری" in seen


@pytest.mark.django_db
def test_narrowing_to_one_of_my_companies_hides_the_other(member, tenant, auth, org, news):
    _member_of(member, org["a1"], tenant)
    CompanyMembership.objects.create(user=member, company=org["b1"])

    both = _titles(Client().get("/api/v1/news", **auth(member, tenant)))
    assert {"خبر شرکت الف-۱", "خبر شرکت ب-۱"} <= both

    headers = {**auth(member, tenant), "HTTP_X_SCOPE_COMPANY": str(org["a1"].id)}
    narrowed = _titles(Client().get("/api/v1/news", **headers))
    assert "خبر شرکت الف-۱" in narrowed
    assert "خبر شرکت ب-۱" not in narrowed


@pytest.mark.django_db
def test_a_scoped_item_cannot_be_fetched_directly_either(member, tenant, auth, org, news):
    """Hiding it from the list is not enough if the detail route still serves it."""
    _member_of(member, org["a1"], tenant)
    res = Client().get(f"/api/v1/news/{news['b1'].id}", **auth(member, tenant))
    assert res.status_code == 404


# ── the endpoint the interface reads ─────────────────────────────────────────
@pytest.mark.django_db
def test_my_scope_describes_the_users_own_reach(member, tenant, auth, org):
    _member_of(member, org["a1"], tenant)
    body = Client().get("/api/v1/my/scope", **auth(member, tenant)).json()["data"]

    assert body["level"] == COMPANY
    assert body["publishable"] == ["شرکت"]
    assert str(org["a1"].id) in body["memberCompanyIds"]
    assert body["role"]["title"]
    assert "news.list" in body["role"]["permissions"]


@pytest.mark.django_db
def test_my_scope_offers_the_whole_tree_to_a_platform_admin(platform_admin, tenant, auth, org):
    body = Client().get("/api/v1/my/scope", **auth(platform_admin, tenant)).json()["data"]
    assert body["level"] == SYSTEM
    assert body["canSwitch"] is True
    labels = [s["label"] for s in body["switchable"]]
    assert "کل سیستم" in labels
    assert "شرکت الف-۱" in labels and "شرکت ب-۱" in labels


@pytest.mark.django_db
def test_my_scope_needs_authentication(tenant):
    assert Client().get("/api/v1/my/scope").status_code == 401


@pytest.mark.django_db
def test_an_ordinary_member_is_company_level_not_group(member, tenant):
    """«عضو عادی» carries a group-scoped role but moderates nothing, so calling
    them group level would mislabel most of the organisation."""
    from apps.tenancy.scope import GROUP

    s = scope_for(member, tenant)
    assert s.level == COMPANY != GROUP


@pytest.mark.django_db
def test_a_group_moderator_is_group_level(member, tenant):
    RoleAssignment.objects.filter(user=member).delete()
    RoleAssignment.objects.create(
        user=member, role=Role.objects.get(key="group-moderator"), tenant=tenant,
    )
    from apps.tenancy.scope import GROUP

    assert scope_for(member, tenant).level == GROUP


@pytest.mark.django_db
def test_the_directory_only_lists_people_in_your_reach(admin, member, tenant, auth, org, django_user_model):
    """A company administrator has no business enumerating another
    subsidiary's staff."""
    outsider = django_user_model.objects.create_user(
        username="beta-person", password="x", name="کارمند ب", tenant=tenant, company=org["b1"],
    )
    _member_of(admin, org["a1"], tenant)
    RoleAssignment.objects.filter(user=admin).delete()
    RoleAssignment.objects.create(
        user=admin, role=Role.objects.get(key="org-admin"), tenant=tenant, company=org["a1"],
    )

    names = {u["name"] for u in Client().get("/api/v1/users", **auth(admin, tenant)).json()["data"]}
    assert "کارمند ب" not in names
    assert outsider.name not in names


@pytest.mark.django_db
def test_a_platform_admin_sees_the_whole_directory(platform_admin, member, tenant, auth, org, django_user_model):
    django_user_model.objects.create_user(
        username="beta-person", password="x", name="کارمند ب", tenant=tenant, company=org["b1"],
    )
    names = {u["name"] for u in Client().get("/api/v1/users", **auth(platform_admin, tenant)).json()["data"]}
    assert "کارمند ب" in names
