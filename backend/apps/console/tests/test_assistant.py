import io
import json

from django.test import Client, override_settings

from apps.projects.models import Project


def test_assistant_answers_from_live_data(admin, tenant, auth):
    Project.objects.create(tenant=tenant, name="پ۱", health="green")
    Project.objects.create(tenant=tenant, name="پ۲", health="red")
    r = Client().post("/api/v1/assistant/ask", json.dumps({"question": "سلامت پورتفولیو چگونه است؟"}),
                      content_type="application/json", **auth(admin, tenant))
    body = r.json()["data"]
    ans = body["answer"]
    assert "سبز" in ans and "قرمز" in ans  # reflects the two live projects
    assert body["source"] == "rules"       # no API key → deterministic matcher


@override_settings(ANTHROPIC_API_KEY="test-key")
def test_assistant_uses_llm_when_key_set(admin, tenant, auth, monkeypatch):
    """With a key configured, the view calls the LLM and returns its answer.
    urlopen is stubbed so the test is hermetic (no network)."""
    captured = {}

    class FakeResp(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["key"] = req.headers.get("X-api-key")
        payload = {"content": [{"type": "text", "text": "پاسخ آزمایشی از مدل زبانی."}]}
        return FakeResp(json.dumps(payload).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    r = Client().post("/api/v1/assistant/ask", json.dumps({"question": "خلاصهٔ وضعیت؟"}),
                      content_type="application/json", **auth(admin, tenant))
    body = r.json()["data"]
    assert body["source"] == "llm" and body["answer"] == "پاسخ آزمایشی از مدل زبانی."
    assert captured["url"].endswith("/v1/messages") and captured["key"] == "test-key"


@override_settings(ANTHROPIC_API_KEY="test-key")
def test_assistant_falls_back_when_llm_errors(admin, tenant, auth, monkeypatch):
    def boom(req, timeout=None):
        raise OSError("network down")

    monkeypatch.setattr("urllib.request.urlopen", boom)
    r = Client().post("/api/v1/assistant/ask", json.dumps({"question": "قراردادها؟"}),
                      content_type="application/json", **auth(admin, tenant))
    assert r.json()["data"]["source"] == "rules"  # graceful fallback


def test_assistant_suggestions(admin, tenant, auth):
    d = Client().get("/api/v1/assistant/suggestions", **auth(admin, tenant)).json()["data"]
    assert isinstance(d["suggestions"], list) and len(d["suggestions"]) >= 3
