"""
Response envelope renderer.

Binding cross-component contract (shared with the PHP backend, enforced by a
CI contract test): every successful response body is

    { "data": <payload>, "links": {...}, "meta": {...} }

The pagination class supplies `links`/`meta` for list endpoints. For detail
and action endpoints we wrap the payload with empty `links`/`meta`. Bodies that
are already enveloped (e.g. built by the pagination class or the exception
handler) are passed through untouched.
"""
from rest_framework.renderers import JSONRenderer

ENVELOPE_KEYS = {"data", "links", "meta"}
ERROR_KEYS = {"error"}


class EnvelopeJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict) and (ENVELOPE_KEYS.issubset(data) or ERROR_KEYS.issubset(data)):
            body = data
        else:
            body = {"data": data, "links": {}, "meta": {}}
        return super().render(body, accepted_media_type, renderer_context)
