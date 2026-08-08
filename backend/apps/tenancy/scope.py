"""Organisational scope: what a user may see, and where they may publish.

Scope follows who a person is, not what they select. It is derived from their
role assignment (which sets the level) and their company memberships (which set
the reach), so a user cannot widen their own view by choosing a different
option in the interface.

This lives on the server for the same reason: the frontend has an identical
model for deciding what to *render*, but rendering is a courtesy. Content
belonging to one subsidiary must not reach another even if the caller crafts
the request by hand, so `visible_q` is applied to the queryset itself.

Levels mirror the product's vocabulary:
    سیستم   — the whole installation
    هلدینگ  — one holding and its companies
    شرکت    — the companies the user belongs to
    گروه    — a single group's moderator
"""
from django.db.models import Q

SYSTEM = "سیستم"
HOLDING = "هلدینگ"
COMPANY = "شرکت"
GROUP = "گروه"

# Content scope values as stored (see core.models.ContentScope).
S_GLOBAL = "global"
S_HOLDING = "holding"
S_COMPANY = "company"


class SessionScope:
    """One user's reach within one tenant."""

    def __init__(self, level, company_ids, holding_ids, role_holding_id=None, role_company_id=None):
        self.level = level
        self.company_ids = list(company_ids)
        self.holding_ids = list(holding_ids)
        self.role_holding_id = role_holding_id
        self.role_company_id = role_company_id

    # ── what the user may publish ────────────────────────────────────────────
    @property
    def publishable(self) -> list[str]:
        if self.level == SYSTEM:
            return ["سراسری", "هلدینگ", "شرکت"]
        if self.level == HOLDING:
            return ["هلدینگ", "شرکت"]
        return ["شرکت"]

    # ── where the user may move between ──────────────────────────────────────
    def switchable(self, holdings, companies) -> list[dict]:
        """The domains this user may look at.

        At system level this is «مشاهده به‌عنوان» over everything. Lower down it
        is only what they already belong to — the switcher never grants reach,
        it only narrows an existing one.
        """
        if self.level == SYSTEM:
            out = [{"label": "کل سیستم"}]
            for h in holdings:
                out.append({"holdingId": str(h.id), "label": h.name})
                out += [
                    {"holdingId": str(h.id), "companyId": str(c.id), "label": c.name}
                    for c in companies if c.holding_id == h.id
                ]
            return out

        if self.level == HOLDING:
            hid = self.role_holding_id or (self.holding_ids[0] if self.holding_ids else None)
            holding = next((h for h in holdings if str(h.id) == str(hid)), None)
            own = [c for c in companies if str(c.holding_id) == str(hid)]
            return [
                {"holdingId": str(hid) if hid else None,
                 "label": f"کل {holding.name}" if holding else "کل هلدینگ"},
                *[{"holdingId": str(hid), "companyId": str(c.id), "label": c.name} for c in own],
            ]

        mine = [c for c in companies if str(c.id) in {str(x) for x in self.company_ids}]
        return [{"holdingId": str(c.holding_id), "companyId": str(c.id), "label": c.name} for c in mine]

    def can_switch(self, holdings, companies) -> bool:
        if self.level == SYSTEM:
            return True
        return len(self.switchable(holdings, companies)) > 1

    # ── what the user may read ───────────────────────────────────────────────
    def visible_q(self, active_holding_id=None, active_company_id=None) -> Q | None:
        """A filter for scoped content, or None when everything is visible.

        Returning None rather than an always-true Q keeps the common
        system-level case free of a pointless WHERE clause.
        """
        if self.level == SYSTEM and not active_holding_id and not active_company_id:
            return None

        # Global content is visible to everyone, always.
        q = Q(scope=S_GLOBAL) | Q(scope="") | Q(scope__isnull=True)

        if active_company_id:
            return q | Q(scope=S_COMPANY, company_id=active_company_id) | (
                Q(scope=S_HOLDING, holding_id=active_holding_id) if active_holding_id else Q(pk__in=[])
            )
        if active_holding_id:
            return q | Q(holding_id=active_holding_id)

        # No explicit selection: everything the user's memberships reach.
        return q | Q(scope=S_HOLDING, holding_id__in=self.holding_ids) \
                 | Q(scope=S_COMPANY, company_id__in=self.company_ids)

    def as_dict(self, holdings, companies) -> dict:
        return {
            "level": self.level,
            "memberCompanyIds": [str(x) for x in self.company_ids],
            "memberHoldingIds": [str(x) for x in self.holding_ids],
            "canSwitch": self.can_switch(holdings, companies),
            "switchable": self.switchable(holdings, companies),
            "publishable": self.publishable,
        }


def _level_for(user, tenant) -> tuple[str, object, object]:
    """The level a user's role assignment gives them, plus any narrowing.

    A platform-scoped role means the whole installation. A tenant role narrowed
    to a holding or company means exactly that. Everything else is company
    level, which is the safe default: a role that says nothing about reach must
    not be read as saying «everything».
    """
    from apps.rbac.models import RoleAssignment

    assignment = (
        RoleAssignment.objects
        .filter(user=user)
        .filter(Q(tenant=tenant) | Q(tenant__isnull=True))
        .select_related("role")
        .order_by("-role__scope")      # platform sorts before group/tenant
        .first()
    )
    if user.is_superuser:
        return SYSTEM, None, None
    if assignment is None:
        return COMPANY, None, None

    role = assignment.role
    if role.scope == "platform":
        return SYSTEM, None, None
    if assignment.company_id:
        return COMPANY, assignment.holding_id, assignment.company_id
    if assignment.holding_id:
        return HOLDING, assignment.holding_id, None
    if role.scope == "group":
        # «گروه» means authority over a group, which only a moderator has. An
        # ordinary member also carries a group-scoped role, and calling them
        # group level would mislabel the majority of the organisation — their
        # reach is simply their company memberships.
        moderates = "groups.members" in (role.permissions or [])
        return (GROUP if moderates else COMPANY), None, None
    # A tenant-wide role with no narrowing runs the organisation.
    return SYSTEM, None, None


def scope_for(user, tenant) -> SessionScope:
    """Resolve one user's scope. Cheap enough to call per request."""
    from .models import Company, CompanyMembership

    level, role_holding, role_company = _level_for(user, tenant)

    company_ids = list(
        CompanyMembership.objects.filter(user=user).values_list("company_id", flat=True)
    )
    # The home company on the user record counts as a membership too, so an
    # account created before the membership table still has a scope.
    if user.company_id and user.company_id not in company_ids:
        company_ids.append(user.company_id)
    if role_company and role_company not in company_ids:
        company_ids.append(role_company)

    holding_ids = list(
        Company.objects.filter(id__in=company_ids).values_list("holding_id", flat=True).distinct()
    )
    if role_holding and role_holding not in holding_ids:
        holding_ids.append(role_holding)

    return SessionScope(level, company_ids, holding_ids, role_holding, role_company)
