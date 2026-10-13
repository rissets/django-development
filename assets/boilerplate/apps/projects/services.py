from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import Project


def _require_actor(actor):
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionDenied("Akun aktif diperlukan.")


def create_project(*, actor, name: str, instance: Project | None = None) -> Project:
    _require_actor(actor)
    project = instance if instance is not None else Project()
    if project.pk is not None:
        raise ValidationError("Create tidak dapat menimpa proyek yang sudah ada.")
    project.owner = actor
    project.name = name.strip()
    project.status = Project.Status.DRAFT
    project.full_clean()
    project.save()
    return project


@transaction.atomic
def update_project(*, actor, project_id: int, name: str) -> Project:
    _require_actor(actor)
    project = Project.objects.visible_to(actor).select_for_update().get(pk=project_id)
    project.name = name.strip()
    project.full_clean()
    project.save(update_fields=["name", "updated_at"])
    return project


@transaction.atomic
def transition_project(*, actor, project_id: int, target: str) -> Project:
    _require_actor(actor)
    project = Project.objects.visible_to(actor).select_for_update().get(pk=project_id)
    allowed = {
        Project.Status.ACTIVE: {Project.Status.DRAFT},
        Project.Status.ARCHIVED: {Project.Status.DRAFT, Project.Status.ACTIVE},
    }
    if target not in allowed:
        raise ValidationError("Tujuan perubahan status tidak didukung.")
    if project.status == target:
        return project
    if project.status not in allowed[target]:
        raise ValidationError("Proyek arsip tidak dapat diaktifkan kembali.")
    project.status = target
    project.full_clean()
    project.save(update_fields=["status", "updated_at"])
    return project
