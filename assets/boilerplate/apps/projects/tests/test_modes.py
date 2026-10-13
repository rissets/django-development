from django.conf import settings
from django.test import TestCase


class ModeTests(TestCase):
    def test_public_health_and_selected_route_surfaces(self):
        self.assertEqual(self.client.get("/health/").json(), {"status": "ok"})
        self.assertEqual(
            self.client.get("/projects/").status_code, 302 if settings.ENABLE_FULLSTACK else 404
        )
        self.assertEqual(
            self.client.get("/api/v1/projects/").status_code, 403 if settings.ENABLE_API else 404
        )
        self.assertEqual(self.client.get("/admin/login/").status_code, 200)
