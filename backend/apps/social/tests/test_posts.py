import json
from django.test import Client

from apps.social.models import Post


def test_post_create_list_and_like_toggle(admin, member, tenant, auth):
    p = Client().post("/api/v1/posts", json.dumps({"content": "سلام تیم", "tags": ["خبر"]}),
                      content_type="application/json", **auth(admin, tenant)).json()["data"]
    assert p["author"]["name"] == admin.name and p["likes"] == 0 and p["my_like"] is False

    r = Client().post(f"/api/v1/posts/{p['id']}/like", **auth(member, tenant)).json()["data"]
    assert r == {"likes": 1, "my_like": True}
    r2 = Client().post(f"/api/v1/posts/{p['id']}/like", **auth(member, tenant)).json()["data"]
    assert r2 == {"likes": 0, "my_like": False}


def test_feed_filters_by_author(admin, member, tenant, auth):
    Post.objects.create(tenant=tenant, author=admin, content="از مدیر")
    Post.objects.create(tenant=tenant, author=member, content="از عضو")
    d = Client().get(f"/api/v1/posts?author={member.id}", **auth(admin, tenant)).json()
    assert d["meta"]["count"] == 1 and d["data"][0]["content"] == "از عضو"


def test_pinned_posts_come_first(admin, tenant, auth):
    Post.objects.create(tenant=tenant, author=admin, content="عادی")
    Post.objects.create(tenant=tenant, author=admin, content="سنجاق", pinned=True)
    d = Client().get("/api/v1/posts", **auth(admin, tenant)).json()["data"]
    assert d[0]["content"] == "سنجاق"
