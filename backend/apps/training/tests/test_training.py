import json

from django.test import Client


def test_course_crud_and_scoping(admin, tenant, auth):
    r = Client().post("/api/v1/training/courses",
                      json.dumps({"title": "دورهٔ امنیت", "instructor": "مدرس", "hours": 8, "capacity": 30}),
                      content_type="application/json", **auth(admin, tenant))
    assert r.status_code == 201 and r.json()["data"]["title"] == "دورهٔ امنیت"
    lst = Client().get("/api/v1/training/courses", **auth(admin, tenant)).json()
    assert lst["meta"]["count"] == 1


def test_courses_need_authentication(db):
    assert Client().get("/api/v1/training/courses").status_code == 401
