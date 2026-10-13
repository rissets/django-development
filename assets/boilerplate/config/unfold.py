import json
from datetime import timedelta

from django.conf import settings
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.html import format_html


def environment_callback(request):
    return [
        "Development" if settings.DEBUG else "Production",
        "warning" if settings.DEBUG else "success",
    ]


def dashboard_callback(request, context):
    from apps.projects.models import Project

    can_view = request.user.has_perm("projects.view_project")
    context["can_view_projects"] = can_view
    if not can_view:
        return context
    context["title"] = "Ringkasan proyek"
    queryset = Project.objects.visible_to(request.user)
    counts = queryset.aggregate(
        total=Count("pk"),
        draft=Count("pk", filter=Q(status="draft")),
        active=Count("pk", filter=Q(status="active")),
    )
    list_url = reverse("admin:projects_project_changelist")
    context["project_metrics"] = [
        {"label": "Seluruh proyek", "value": counts["total"], "href": list_url},
        {"label": "Draft", "value": counts["draft"], "href": list_url + "?status__exact=draft"},
        {"label": "Aktif", "value": counts["active"], "href": list_url + "?status__exact=active"},
    ]
    today = timezone.localdate()
    dates = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    activity = dict(
        queryset.filter(created_at__date__gte=dates[0])
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("pk"))
        .values_list("day", "total")
    )
    context["project_trend"] = json.dumps(
        {
            "labels": [day.isoformat() for day in dates],
            "datasets": [
                {
                    "label": "Proyek dibuat",
                    "data": [activity.get(day, 0) for day in dates],
                    "displayYAxis": True,
                    "borderColor": "#1d4ed8",
                    "backgroundColor": "#93c5fd",
                }
            ],
        }
    )
    context["project_trend_options"] = json.dumps(
        {"scales": {"y": {"beginAtZero": True, "ticks": {"precision": 0}}}}
    )
    context["project_activity"] = [{"date": day, "count": activity.get(day, 0)} for day in dates]
    context["recent_projects"] = {
        "headers": ["Proyek", "Status", "Diperbarui"],
        "rows": [
            [
                format_html(
                    '<a href="{}">{}</a>',
                    reverse("admin:projects_project_change", args=[p.pk]),
                    p.name,
                ),
                p.get_status_display(),
                date_format(timezone.localtime(p.updated_at), "d M Y H:i"),
            ]
            for p in queryset.order_by("-updated_at", "-pk")[:10]
        ],
    }
    context["dashboard_as_of"] = timezone.now()
    return context


def get_unfold_config(app_name):
    return {
        "SITE_TITLE": app_name,
        "SITE_HEADER": app_name,
        "SITE_FAVICONS": [
            {
                "rel": "icon",
                "type": "image/svg+xml",
                "href": lambda request: static("images/mark.svg"),
            }
        ],
        "ENVIRONMENT": "config.unfold.environment_callback",
        "DASHBOARD_CALLBACK": "config.unfold.dashboard_callback",
        "SIDEBAR": {
            "show_search": True,
            "navigation": [
                {
                    "title": "Operasional",
                    "items": [
                        {
                            "title": "Ringkasan",
                            "icon": "dashboard",
                            "link": reverse_lazy("admin:index"),
                        },
                        {
                            "title": "Proyek",
                            "icon": "folder",
                            "link": reverse_lazy("admin:projects_project_changelist"),
                            "permission": lambda request: request.user.has_perm(
                                "projects.view_project"
                            ),
                        },
                        {
                            "title": "Analisis proyek",
                            "icon": "analytics",
                            "link": reverse_lazy("admin:projects_project_summary"),
                            "permission": lambda request: request.user.has_perm(
                                "projects.view_project"
                            ),
                        },
                        {
                            "title": "Pengguna",
                            "icon": "group",
                            "link": reverse_lazy("admin:accounts_user_changelist"),
                            "permission": lambda request: request.user.is_superuser,
                        },
                    ],
                }
            ],
        },
        "COMMAND": {"search_models": False, "show_history": False},
    }
