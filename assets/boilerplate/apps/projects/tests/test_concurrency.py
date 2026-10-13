from concurrent.futures import ThreadPoolExecutor
from threading import Event
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.db import OperationalError, connection, connections, transaction
from django.test import TransactionTestCase

from apps.projects.models import Project
from apps.projects.services import create_project, transition_project


@skipUnless(connection.vendor == "postgresql", "PostgreSQL row-lock proof requires PostgreSQL")
class PostgreSQLLockTests(TransactionTestCase):
    def test_transition_waits_for_locked_row(self):
        owner = get_user_model().objects.create_user(username="lock-owner")
        project = create_project(actor=owner, name="Locked project")
        locked, release = Event(), Event()

        def hold_row():
            try:
                with transaction.atomic():
                    Project.objects.select_for_update().get(pk=project.pk)
                    locked.set()
                    if not release.wait(5):
                        raise AssertionError("Lock test release timed out")
            finally:
                connections.close_all()

        def attempt_transition():
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET lock_timeout = '250ms'")
                transition_project(actor=owner, project_id=project.pk, target="active")
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            holder = pool.submit(hold_row)
            try:
                self.assertTrue(locked.wait(3))
                blocked = pool.submit(attempt_transition)
                with self.assertRaises(OperationalError) as raised:
                    blocked.result(timeout=3)
                self.assertIn("lock timeout", str(raised.exception))
            finally:
                release.set()
            holder.result(timeout=3)
        transition_project(actor=owner, project_id=project.pk, target="active")
        project.refresh_from_db()
        self.assertEqual(project.status, "active")
