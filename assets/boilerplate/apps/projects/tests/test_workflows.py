from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.projects.models import Project
from apps.projects.services import create_project, transition_project, update_project


class WorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user(username="owner")
        cls.other = User.objects.create_user(username="other")
        cls.inactive = User.objects.create_user(username="inactive", is_active=False)
        cls.project = create_project(actor=cls.owner, name="Project A")

    def test_create_strips_and_assigns_trusted_owner(self):
        project = create_project(actor=self.owner, name="  New project  ")
        self.assertEqual(
            (project.name, project.owner_id, project.status),
            ("New project", self.owner.pk, "draft"),
        )

    def test_invalid_names_do_not_persist(self):
        for name in (" ", "x" * 121):
            with self.subTest(name_length=len(name)), self.assertRaises(ValidationError):
                create_project(actor=self.owner, name=name)
        self.assertEqual(Project.objects.count(), 1)

    def test_inactive_actor_is_denied_at_shared_boundary(self):
        self.assertFalse(Project.objects.visible_to(self.inactive).exists())
        with self.assertRaises(PermissionDenied):
            create_project(actor=self.inactive, name="Denied")
        with self.assertRaises(PermissionDenied):
            transition_project(actor=self.inactive, project_id=self.project.pk, target="active")

    def test_other_owner_cannot_read_update_or_transition(self):
        self.assertFalse(Project.objects.visible_to(self.other).exists())
        with self.assertRaises(Project.DoesNotExist):
            update_project(actor=self.other, project_id=self.project.pk, name="Hijack")
        with self.assertRaises(Project.DoesNotExist):
            transition_project(actor=self.other, project_id=self.project.pk, target="active")

    def test_transition_is_idempotent_and_archived_cannot_reactivate(self):
        transition_project(actor=self.owner, project_id=self.project.pk, target="active")
        before = Project.objects.get(pk=self.project.pk).updated_at
        transition_project(actor=self.owner, project_id=self.project.pk, target="active")
        self.assertEqual(Project.objects.get(pk=self.project.pk).updated_at, before)
        transition_project(actor=self.owner, project_id=self.project.pk, target="archived")
        with self.assertRaises(ValidationError):
            transition_project(actor=self.owner, project_id=self.project.pk, target="active")
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, "archived")

    def test_unknown_target_and_existing_instance_do_not_overwrite(self):
        with self.assertRaises(ValidationError):
            transition_project(actor=self.owner, project_id=self.project.pk, target="unexpected")
        with self.assertRaises(ValidationError):
            create_project(actor=self.other, name="Overwrite", instance=self.project)
        self.project.refresh_from_db()
        self.assertEqual(self.project.owner_id, self.owner.pk)

    def test_database_constraints_cover_direct_writes(self):
        for field, value in (("name", ""), ("status", "invalid")):
            with self.subTest(field=field), self.assertRaises(IntegrityError), transaction.atomic():
                Project.objects.filter(pk=self.project.pk).update(**{field: value})

    def test_failed_update_keeps_previous_state(self):
        with self.assertRaises(ValidationError):
            update_project(actor=self.owner, project_id=self.project.pk, name=" ")
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Project A")
