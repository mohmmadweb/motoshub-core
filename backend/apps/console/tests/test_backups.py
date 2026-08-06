"""Manual backups: permissions, listing, and path safety."""
import pytest
from django.test import Client

from apps.console import backups


@pytest.fixture
def backup_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(backups, "BACKUP_DIR", tmp_path)
    return tmp_path


@pytest.mark.django_db
def test_listing_requires_the_storage_permission(admin, member, platform_admin, tenant, auth, backup_dir):
    assert Client().get("/api/v1/settings/backups", **auth(member, tenant)).status_code == 403
    assert Client().get("/api/v1/settings/backups", **auth(admin, tenant)).status_code == 403
    assert Client().get("/api/v1/settings/backups", **auth(platform_admin, tenant)).status_code == 200


@pytest.mark.django_db
def test_listing_reports_real_files_newest_first(platform_admin, tenant, auth, backup_dir):
    (backup_dir / "motoshub-20260101-010101.sql.gz").write_bytes(b"x" * 2048)
    (backup_dir / "motoshub-20260202-020202.sql.gz").write_bytes(b"y" * 4096)
    (backup_dir / "unrelated.txt").write_bytes(b"ignore me")

    rows = Client().get("/api/v1/settings/backups", **auth(platform_admin, tenant)).json()["data"]["backups"]
    assert [r["name"] for r in rows] == [
        "motoshub-20260202-020202.sql.gz",
        "motoshub-20260101-010101.sql.gz",
    ]
    assert rows[0]["size"] == 4096


@pytest.mark.django_db
def test_sqlite_deployments_are_told_plainly(platform_admin, tenant, auth, backup_dir):
    """The test database is sqlite, so taking a dump is refused with a reason
    rather than failing obscurely."""
    res = Client().post("/api/v1/settings/backups", **auth(platform_admin, tenant))
    assert res.status_code == 422
    assert "PostgreSQL" in res.json()["error"]["message"]


@pytest.mark.django_db
@pytest.mark.parametrize("name", [
    "../../etc/passwd",
    "..%2F..%2Fetc%2Fpasswd",
    "motoshub-20260101-010101.sql.gz.part",   # an unfinished dump is not a backup
    "arbitrary.sql.gz",
])
def test_download_refuses_anything_but_a_generated_name(platform_admin, tenant, auth, backup_dir, name):
    res = Client().get(f"/api/v1/settings/backups/{name}", **auth(platform_admin, tenant))
    assert res.status_code in (404, 301, 400)


@pytest.mark.django_db
def test_download_and_delete_round_trip(platform_admin, tenant, auth, backup_dir):
    f = backup_dir / "motoshub-20260303-030303.sql.gz"
    f.write_bytes(b"z" * 1500)
    headers = auth(platform_admin, tenant)

    res = Client().get(f"/api/v1/settings/backups/{f.name}", **headers)
    assert res.status_code == 200
    assert b"".join(res.streaming_content) == b"z" * 1500

    assert Client().delete(f"/api/v1/settings/backups/{f.name}", **headers).status_code == 204
    assert not f.exists()
