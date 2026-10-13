from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin

from config.unfold import dashboard_callback


class ProjectSummaryView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Ringkasan proyek"
    permission_required = ("projects.view_project",)
    template_name = "admin/projects/summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return dashboard_callback(self.request, context)
