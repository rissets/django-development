from django.conf import settings
from django.db import models


class ProjectQuerySet(models.QuerySet):
    def visible_to(self, actor):
        if not actor.is_authenticated or not actor.is_active:
            return self.none()
        if actor.is_superuser:
            return self
        return self.filter(owner=actor)


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Aktif"
        ARCHIVED = "archived", "Diarsipkan"

    name = models.CharField("Nama proyek", max_length=120)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ProjectQuerySet.as_manager()

    class Meta:
        verbose_name = "Proyek"
        verbose_name_plural = "Proyek"
        ordering = ("-created_at", "-pk")
        constraints = [
            models.CheckConstraint(condition=~models.Q(name=""), name="project_name_present"),
            models.CheckConstraint(
                condition=models.Q(status__in=["draft", "active", "archived"]),
                name="project_status_valid",
            ),
        ]

    def __str__(self):
        return self.name
