from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.health import HealthView
from apps.core.uploads import UploadView

api_v1 = [
    path("health", HealthView.as_view(), name="health"),
    path("uploads", UploadView.as_view(), name="upload"),
    path("", include("apps.accounts.urls")),
    path("", include("apps.rbac.urls")),
    path("", include("apps.tenancy.urls")),
    path("", include("apps.content.urls")),
    path("", include("apps.social.urls")),
    path("", include("apps.projects.urls")),
    path("", include("apps.contracts.urls")),
    path("", include("apps.fund.urls")),
    path("", include("apps.training.urls")),
    path("", include("apps.support.urls")),
    path("", include("apps.polls.urls")),
    path("", include("apps.research.urls")),
    path("", include("apps.awards.urls")),
    path("", include("apps.notifications.urls")),
    path("", include("apps.chat.urls")),
    path("", include("apps.competitions.urls")),
    path("", include("apps.console.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1, "api"), namespace="v1")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
]

# In development Django serves uploads itself; in production nginx serves the
# shared media volume directly (see infra/docker-compose.yml).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
