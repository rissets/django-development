from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.projects.models import Project
from apps.projects.services import create_project

PASSWORD = "Local-test-password-42!"


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.operator = User.objects.create_user(
            username="operator", password=PASSWORD, is_staff=True
        )
        cls.operator.user_permissions.set(
            Permission.objects.filter(content_type__app_label="projects")
        )
        cls.other = User.objects.create_user(username="other")
        cls.unprivileged = User.objects.create_user(
            username="staff", password=PASSWORD, is_staff=True
        )
        cls.root = User.objects.create_superuser(username="root", password=PASSWORD)
        cls.own = create_project(actor=cls.operator, name="Operator record")
        cls.foreign = create_project(actor=cls.other, name="Private other record")

    def setUp(self):
        self.client.login(username="operator", password=PASSWORD)

    def test_dashboard_list_detail_and_custom_page_scoped(self):
        for path in ("/admin/", "/admin/projects/project/", "/admin/projects/project/summary/"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Operator record")
            if path != "/admin/projects/project/":
                self.assertRegex(
                    response.content.decode(), r"<title>[\s\S]*Ringkasan proyek[\s\S]*</title>"
                )
                self.assertContains(response, "Data aktivitas")
            self.assertNotContains(response, "Private other record")
        self.assertEqual(
            self.client.get(
                reverse("admin:projects_project_change", args=[self.own.pk])
            ).status_code,
            200,
        )
        self.assertNotEqual(
            self.client.get(
                reverse("admin:projects_project_change", args=[self.foreign.pk])
            ).status_code,
            200,
        )

    def test_create_edit_use_shared_domain_and_owner_is_trusted(self):
        response = self.client.post(
            reverse("admin:projects_project_add"),
            {"name": "Admin create", "owner": self.other.pk, "status": "active", "_save": "Save"},
        )
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(name="Admin create")
        self.assertEqual((project.owner_id, project.status), (self.operator.pk, "draft"))
        self.client.post(
            reverse("admin:projects_project_change", args=[project.pk]),
            {"name": "Admin edit", "status": "archived", "_save": "Save"},
        )
        project.refresh_from_db()
        self.assertEqual((project.name, project.status), ("Admin edit", "draft"))

    def test_bulk_action_does_not_touch_other_scope(self):
        self.client.post(
            reverse("admin:projects_project_changelist"),
            {"action": "activate_selected", "_selected_action": [self.own.pk, self.foreign.pk]},
        )
        self.own.refresh_from_db()
        self.foreign.refresh_from_db()
        self.assertEqual((self.own.status, self.foreign.status), ("active", "draft"))

    def test_dialog_validation_and_execution(self):
        url = reverse("admin:projects_project_activate_dialog", args=[self.own.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        invalid = self.client.post(url, {"_form_submitted": "on"}, HTTP_HX_REQUEST="true")
        self.assertEqual(invalid.status_code, 200)
        self.own.refresh_from_db()
        self.assertEqual(self.own.status, "draft")
        response = self.client.post(
            url, {"confirm": "on", "_form_submitted": "on"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("HX-Redirect", response.headers)
        self.own.refresh_from_db()
        self.assertEqual(self.own.status, "active")

    def test_identity_admin_remains_superuser_only(self):
        self.operator.user_permissions.add(
            *Permission.objects.filter(content_type__app_label="accounts")
        )
        self.assertEqual(self.client.get("/admin/accounts/user/").status_code, 403)
        self.client.login(username="root", password=PASSWORD)
        for url in (
            "/admin/accounts/user/",
            "/admin/accounts/user/add/",
            reverse("admin:accounts_user_change", args=[self.operator.pk]),
        ):
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_custom_page_and_dialog_reject_staff_without_grant(self):
        self.client.login(username="staff", password=PASSWORD)
        self.assertEqual(self.client.get("/admin/projects/project/summary/").status_code, 403)
        self.assertEqual(
            self.client.post(
                reverse("admin:projects_project_activate_dialog", args=[self.own.pk]),
                {"confirm": "on"},
            ).status_code,
            403,
        )
