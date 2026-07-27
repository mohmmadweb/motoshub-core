from django.test import Client

from apps.notifications.models import Notification


def test_user_sees_only_own_notifications(admin, member, tenant, auth):
    Notification.objects.create(tenant=tenant, user=admin, text="مالِ ادمین")
    Notification.objects.create(tenant=tenant, user=member, text="مالِ عضو")
    data = Client().get("/api/v1/notifications/unread_count", **auth(admin, tenant)).json()["data"]
    assert data["count"] == 1
