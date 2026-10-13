from unittest import skipUnless

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.projects.models import Project
from apps.projects.services import create_project

PASSWORD = "Local-test-password-42!"


@skipUnless(settings.ENABLE_FULLSTACK, "HTML routes disabled in API mode")
class HtmlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user(
            username="owner", password=PASSWORD, email="owner@example.test"
        )
        cls.other = User.objects.create_user(username="other", password=PASSWORD)
        cls.project = create_project(actor=cls.owner, name="Owner project")

    def test_credential_login_and_csrf_protected_write_logout(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.get(reverse("projects:list")).status_code, 302)
        client.get(reverse("login"))
        denied = client.post(reverse("login"), {"username": "owner", "password": PASSWORD})
        self.assertEqual(denied.status_code, 403)
        token = client.cookies["csrftoken"].value
        result = client.post(
            reverse("login"),
            {"username": "owner", "password": PASSWORD, "csrfmiddlewaretoken": token},
        )
        self.assertEqual(result.status_code, 302)
        self.assertEqual(
            client.post(reverse("projects:create"), {"name": "Denied"}).status_code, 403
        )
        token = client.cookies["csrftoken"].value
        result = client.post(
            reverse("projects:create"), {"name": "CSRF project", "csrfmiddlewaretoken": token}
        )
        self.assertEqual(result.status_code, 302)
        self.assertEqual(Project.objects.get(name="CSRF project").owner_id, self.owner.pk)
        self.assertEqual(client.get(reverse("logout")).status_code, 405)
        result = client.post(reverse("logout"), {"csrfmiddlewaretoken": token})
        self.assertEqual(result.status_code, 302)
        self.assertEqual(client.get(reverse("projects:list")).status_code, 302)

    def test_invalid_valid_edit_and_transition(self):
        self.client.login(username="owner", password=PASSWORD)
        invalid = self.client.post(reverse("projects:create"), {"name": " "})
        self.assertEqual(invalid.status_code, 200)
        self.assertTrue(invalid.context["form"].errors)
        response = self.client.post(
            reverse("projects:create"),
            {"name": "New project", "owner": self.other.pk, "status": "archived"},
        )
        project = Project.objects.get(name="New project")
        self.assertRedirects(response, reverse("projects:detail", args=[project.pk]))
        self.assertEqual((project.owner_id, project.status), (self.owner.pk, "draft"))
        self.client.post(reverse("projects:edit", args=[project.pk]), {"name": "Renamed"})
        self.client.post(reverse("projects:activate", args=[project.pk]))
        project.refresh_from_db()
        self.assertEqual((project.name, project.status), ("Renamed", "active"))

    def test_other_owner_denied_and_get_cannot_mutate(self):
        self.client.login(username="other", password=PASSWORD)
        for url in (
            reverse("projects:detail", args=[self.project.pk]),
            reverse("projects:edit", args=[self.project.pk]),
        ):
            self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(
            self.client.post(reverse("projects:activate", args=[self.project.pk])).status_code, 404
        )
        self.client.login(username="owner", password=PASSWORD)
        self.assertEqual(
            self.client.get(reverse("projects:activate", args=[self.project.pk])).status_code, 405
        )
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, "draft")

    def test_search_pagination_and_invalid_filter(self):
        self.client.login(username="owner", password=PASSWORD)
        Project.objects.bulk_create(
            [Project(owner=self.owner, name=f"Search {i}") for i in range(30)]
        )
        result = self.client.get(reverse("projects:list"), {"q": "Search", "page": 2})
        self.assertEqual(len(result.context["page_obj"]), 5)
        self.assertEqual(result.context["page_obj"].paginator.count, 30)
        invalid = self.client.get(reverse("projects:list"), {"status": "unknown"})
        self.assertTrue(invalid.context["filters"].errors)
        self.assertEqual(invalid.context["page_obj"].paginator.count, 0)

    def test_password_reset_pages_and_email_locally(self):
        from django.core import mail

        response = self.client.post(reverse("password_reset"), {"email": "owner@example.test"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/reset/", mail.outbox[0].body)

    def test_escaped_project_title_and_nonexistent_page(self):
        self.client.login(username="owner", password=PASSWORD)
        project = create_project(actor=self.owner, name='<script>alert("x")</script>')
        response = self.client.get(reverse("projects:detail", args=[project.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, '<script>alert("x")</script>')
        self.assertEqual(self.client.get("/does-not-exist/").status_code, 404)
