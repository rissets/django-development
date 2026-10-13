from unittest import skipUnless

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.projects.services import create_project

PASSWORD = "Local-test-password-42!"


@skipUnless(settings.ENABLE_API, "API routes disabled in fullstack mode")
class ApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user(username="owner", password=PASSWORD)
        cls.other = User.objects.create_user(username="other", password=PASSWORD)
        cls.project = create_project(actor=cls.owner, name="API project")

    def setUp(self):
        self.api = APIClient(enforce_csrf_checks=True)
        self.api.get("/api-auth/login/")
        token = self.api.cookies["csrftoken"].value
        response = self.api.post(
            "/api-auth/login/",
            {"username": "owner", "password": PASSWORD, "csrfmiddlewaretoken": token},
        )
        self.assertEqual(response.status_code, 302)
        self.token = self.api.cookies["csrftoken"].value

    def test_csrf_create_patch_and_controlled_transition(self):
        self.assertEqual(
            self.api.post("/api/v1/projects/", {"name": "Denied"}, format="json").status_code, 403
        )
        response = self.api.post(
            "/api/v1/projects/",
            {"name": "New", "owner": self.other.pk, "status": "archived"},
            format="json",
            HTTP_X_CSRFTOKEN=self.token,
        )
        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(pk=response.data["id"])
        self.assertEqual((project.owner_id, project.status), (self.owner.pk, "draft"))
        url = f"/api/v1/projects/{project.pk}/"
        response = self.api.patch(
            url,
            {"name": "Renamed", "status": "archived"},
            format="json",
            HTTP_X_CSRFTOKEN=self.token,
        )
        self.assertEqual((response.status_code, response.data["status"]), (200, "draft"))
        self.assertEqual(
            self.api.post(
                url + "activate/", {}, format="json", HTTP_X_CSRFTOKEN=self.token
            ).status_code,
            200,
        )
        self.api.post(url + "archive/", {}, format="json", HTTP_X_CSRFTOKEN=self.token)
        self.assertEqual(
            self.api.post(
                url + "activate/", {}, format="json", HTTP_X_CSRFTOKEN=self.token
            ).status_code,
            400,
        )

    def test_other_actor_cannot_read_edit_or_activate(self):
        other = APIClient()
        other.login(username="other", password=PASSWORD)
        url = f"/api/v1/projects/{self.project.pk}/"
        self.assertEqual(other.get(url).status_code, 404)
        self.assertEqual(other.patch(url, {"name": "Hijack"}, format="json").status_code, 404)
        self.assertEqual(other.post(url + "activate/").status_code, 404)
        self.assertEqual(other.get("/api/v1/projects/").data["count"], 0)

    def test_anonymous_docs_and_api_denied(self):
        anonymous = APIClient()
        for path in ("/api/v1/projects/", "/api/docs/", "/api/schema/"):
            self.assertEqual(anonymous.get(path).status_code, 403)
        self.assertEqual(self.api.get("/api/docs/").status_code, 403)

    def test_input_filter_pagination_and_content_type(self):
        url = "/api/v1/projects/"
        self.assertEqual(
            self.api.post(
                url, {"name": " "}, format="json", HTTP_X_CSRFTOKEN=self.token
            ).status_code,
            400,
        )
        self.assertEqual(self.api.get(url, {"status": "invalid"}).status_code, 400)
        Project.objects.bulk_create(
            [Project(owner=self.owner, name=f"Page {i}") for i in range(30)]
        )
        self.assertEqual(len(self.api.get(url, {"q": "Page", "page": 2}).data["results"]), 5)
        bad = self.api.post(
            url, "not-json", content_type="application/json", HTTP_X_CSRFTOKEN=self.token
        )
        self.assertEqual(bad.status_code, 400)
