# Pengujian dan security boundaries

Panduan ini untuk menentukan evidence yang bermakna pada perubahan Django. Follow repository/user conventions; jangan menambah suite besar untuk perubahan kecil. Admin-only testing convention tetap mengikuti skill admin yang dipakai kecuali user/repo meminta tests.

## Jenis pengujian

| Layer | Test yang bermakna | Bukan bukti |
|---|---|---|
| Pure rule/function | Boundary values/error, rounding/state math | Invariant seluruh entrypoint jika callernya berbeda |
| Workflow/model/DB | Constraints, rollback, permissions, persisted state | PostgreSQL locks bila dijalankan SQLite |
| Django HTML | Bound invalid/valid form, redirect, content, scope, CSRF bila dibutuhkan | Actual keyboard/browser interaction |
| DRF | Identity, denied scope, payload/status, validation, pagination | Semua endpoint benar hanya karena schema valid |
| Unfold | Registration, role/object rights, form/action/custom route behavior | Styling browser hanya karena server merender HTML |
| External integration | Request/response mapping with double | Real provider credentials/delivery |
| Worker | Task logic/eager test | Real broker consumer/retry/result |
| Browser E2E | Authenticated user journey and persistence | Entire application coverage from one flow |

Test the risk that motivated the change. Reuse runner, fixtures, factories and existing acceptance path. Avoid implementation-mirroring asserts that only restate which method was called or a class name when user-visible behavior matters.

## Regression test contoh

Melanjutkan Project example, Django TestCase ini menguji owner denial dan idempotent transition. Database ini tidak membuktikan concurrent row locks.

```python
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.projects.models import Project
from apps.projects.services import activate_project, create_project


class ProjectWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user(username="owner")
        cls.other = User.objects.create_user(username="other")

    def test_other_actor_cannot_activate_project(self):
        project = create_project(actor=self.owner, name="Example")
        with self.assertRaises(Project.DoesNotExist):
            activate_project(actor=self.other, project_id=project.pk)
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.DRAFT)

    def test_repeated_activation_keeps_active_state(self):
        project = create_project(actor=self.owner, name="Example")
        activate_project(actor=self.owner, project_id=project.pk)
        activate_project(actor=self.owner, project_id=project.pk)
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.ACTIVE)
```

Add meaningful API/HTML tests for adapter mapping and denied related choices rather than duplicate all service tests in each layer. If activation eventually creates audit/payment/job effects, assert duplication behavior as well, not state alone.

## Auth dan CSRF tests

DRF force_authenticate/client.force_login isolate authorization logic; they bypass parts of real login credentials/session lifecycle. Use actual login flow when that is acceptance. Django client does not enforce CSRF by default; use `Client(enforce_csrf_checks=True)` or appropriate API client for CSRF boundary cases. Do not infer CSRF coverage from a successful POST in the default client.

Anonymous denial, authenticated wrong role, right role wrong tenant, correct tenant wrong relation, inactive identity, and expiry are distinct cases. A superuser-only smoke test does not verify tenant/staff roles. Direct custom URL/action/autocomplete/export tests catch UI-only permissions.

## Database and callbacks

TestCase transaction wrapping differs from commit-running TransactionTestCase. For on_commit use callback capture/execution when testing enqueue logic; use actual transaction/worker tests if real delivery is required. DB test setup must match feature requirements; multi-DB routers/read-only databases need isolated policy-aware fixtures, not accidental production reads/writes.

Use PostgreSQL for lock/isolation/database-specific assertions, separate connections when verifying concurrency, bounded synchronization/timeouts, and explicit expected final state. SQLite/in-memory checks can cover ordinary logic but must be labeled accordingly.

## Trust boundary checklist

- Incoming body/query/file/headers parsed and validated before use; no arbitrary ORM lookup names or SQL identifiers from user input.
- Owner/tenant/privilege assigned from trusted identity/context, relation targets scoped.
- Session unsafe methods have CSRF; CORS origins/credentials deliberate; safe redirects.
- HTML autoescape preserved; rich content sanitized; JSON serialization does not bypass escaping.
- Private files/schema/docs/export endpoints protected server-side.
- Admin actions/custom pages/suggestions/datasets enforce permissions even by direct request.
- Webhook signatures/auth checked before side effects; replay/idempotency where necessary.
- Secrets absent from source, response, logs, fixtures, and reports; production settings fail closed for missing required values.
- Cookie/proxy/CSP/security settings correspond to actual topology; no global exemptions to hide errors.

This checklist complements implementation, not an unsolicited compliance audit. Apply controls relevant to the task and data; do not invent regulatory assertions.

## Fixture quality dan test doubles

Fixtures should represent constraints/relations and role/scope realistically. Label synthetic data. Tests should not pass solely because every object belongs to the superuser. Isolate external calls using provider-boundary doubles; exercise expected malformed/error/timeouts and assert meaningful state/retry behavior. Mock does not prove live provider availability.

Avoid snapshots for volatile timestamps/IDs without normalization. Assertions focus on semantic outcomes, not every class/spacing detail. Accessibility tools and browser checks evaluate different failure modes; keyboard/focus/content error handling still matters.

## Evidence record

Report settings/runtime/DB mode without secrets, commands and outcome, actor/path exercised, negative cases, actual persisted result, and limits. Separate resolver/import/schema/check success, server-client integration checks, browser E2E, and production/provider verification. Keep failures visible and fix them before declaring the requested path complete.
