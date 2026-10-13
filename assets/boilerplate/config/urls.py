from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from config.views import health

urlpatterns = [path("health/", health, name="health"), path("admin/", admin.site.urls)]
if settings.ENABLE_FULLSTACK:
    urlpatterns += [
        path("", RedirectView.as_view(pattern_name="projects:list", permanent=False)),
        path("accounts/", include("django.contrib.auth.urls")),
        path("projects/", include("apps.projects.urls")),
    ]
else:
    urlpatterns += [path("", RedirectView.as_view(pattern_name="admin:index", permanent=False))]
if settings.ENABLE_API:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

    urlpatterns += [
        path("api/v1/", include("apps.projects.api.urls")),
        path("api-auth/", include("rest_framework.urls")),
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="api-docs"),
    ]
