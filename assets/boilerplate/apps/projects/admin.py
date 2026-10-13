from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponse
from django.urls import path, reverse
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateTimeFilter
from unfold.decorators import action, display
from unfold.forms import BaseDialogForm

from .admin_views import ProjectSummaryView
from .models import Project
from .services import create_project, transition_project, update_project


class ActivationConfirmationForm(BaseDialogForm):
    confirm = forms.BooleanField(label="Saya ingin mengaktifkan proyek ini.", required=True)


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ("name", "status_label", "owner", "updated_at")
    search_fields = ("name",)
    list_filter = ("status", ("created_at", RangeDateTimeFilter))
    list_filter_submit = True
    list_select_related = ("owner",)
    list_per_page = 25
    readonly_fields = ("owner", "status", "created_at", "updated_at")
    fields = ("name", "owner", "status", "created_at", "updated_at")
    warn_unsaved_form = True
    actions = ("activate_selected",)
    actions_detail = ("activate_dialog",)

    def get_queryset(self, request):
        return super().get_queryset(request).visible_to(request.user)

    def has_change_permission(self, request, obj=None):
        allowed = super().has_change_permission(request, obj)
        return allowed and (obj is None or self.get_queryset(request).filter(pk=obj.pk).exists())

    def has_delete_permission(self, request, obj=None):
        # Baseline lifecycle memakai archive; penghapusan membutuhkan policy produk tersendiri.
        return False

    def save_model(self, request, obj, form, change):
        if change:
            update_project(actor=request.user, project_id=obj.pk, name=obj.name)
            obj.refresh_from_db()
        else:
            create_project(actor=request.user, name=obj.name, instance=obj)

    @display(
        description="Status", label={"draft": "warning", "active": "success", "archived": "info"}
    )
    def status_label(self, obj):
        return obj.status

    @admin.action(description="Aktifkan proyek terpilih", permissions=["change"])
    def activate_selected(self, request, queryset):
        # Batch dibatasi agar tidak menahan banyak transaksi pada satu request.
        if queryset.count() > 100:
            self.message_user(request, "Pilih maksimal 100 proyek.", messages.ERROR)
            return
        succeeded = failed = 0
        for project in queryset:
            if not self.has_change_permission(request, project):
                failed += 1
                continue
            try:
                transition_project(actor=request.user, project_id=project.pk, target="active")
            except (ValidationError, Project.DoesNotExist):
                failed += 1
            else:
                succeeded += 1
        self.message_user(
            request,
            f"{succeeded} berhasil; {failed} tidak diproses.",
            messages.WARNING if failed else messages.SUCCESS,
        )

    @action(
        description="Aktifkan proyek",
        permissions=["activate_dialog"],
        dialog={"title": "Aktifkan proyek", "form_class": ActivationConfirmationForm},
    )
    def activate_dialog(self, request, form, object_id):
        project = self.get_object(request, object_id)
        if project is None:
            raise Http404
        if request.method != "POST" or not self.has_change_permission(request, project):
            raise PermissionDenied
        try:
            transition_project(actor=request.user, project_id=project.pk, target="active")
        except Project.DoesNotExist as error:
            raise Http404 from error
        except ValidationError as error:
            self.message_user(request, " ".join(error.messages), messages.ERROR)
        else:
            self.message_user(request, "Proyek berhasil diaktifkan.", messages.SUCCESS)
        url = reverse("admin:projects_project_change", args=[project.pk])
        return HttpResponse(headers={"HX-Redirect": url})

    def has_activate_dialog_permission(self, request, object_id):
        project = self.get_object(request, object_id)
        return (
            project is not None
            and self.has_change_permission(request, project)
            and project.status == Project.Status.DRAFT
        )

    def get_urls(self):
        view = self.admin_site.admin_view(ProjectSummaryView.as_view(model_admin=self))
        return [path("summary/", view, name="projects_project_summary")] + super().get_urls()
