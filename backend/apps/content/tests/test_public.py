from django.test import Client

from apps.content.models import News


def test_public_feed_is_unauthenticated_and_public_only(admin, tenant, auth):
    News.objects.create(tenant=tenant, title="عمومی", visibility="public", author=admin)
    News.objects.create(tenant=tenant, title="خصوصی", visibility="private", author=admin)
    r = Client().get("/api/v1/public/feed")  # no auth
    assert r.status_code == 200
    titles = [n["title"] for n in r.json()["data"]["news"]]
    assert "عمومی" in titles and "خصوصی" not in titles
