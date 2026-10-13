---
name: django-development
description: Build, extend, refactor, or review Django applications and Python code, including server-rendered fullstack features, Django REST Framework APIs, ORM models and migrations, deployment configuration, and Django Unfold admin. Use for Django implementation tasks; preserve existing architecture and match installed package versions.
metadata:
  version: "0.1.0"
  short-description: Django fullstack and REST API with Unfold admin
---

# Django Development

Deliver the requested Django user path with coherent data, permissions, UI/API contracts, and evidence. This user's admin standard is **Django Unfold**, including API-only projects that expose an admin. Do not substitute another admin theme. Follow the user's language for explanations and repository conventions for code.

## Start with the actual project

1. Read applicable repository instructions, architecture, requirements, and existing implementations. Inspect manifests/locks, Python/Django/package versions, settings entrypoints, database, URL namespaces, auth model, admin registration, templates/frontend, static/media storage, and test commands. Do not print secrets or dump resolved settings.
2. Identify affected surfaces: HTML, JSON API, admin, background work, deployment. Preserve existing services and design. For a new project choose the smallest coherent stack using [packages](references/packages.md); do not install every listed dependency.
3. Read the relevant reference below. Check official docs matching installed versions before using version-sensitive APIs. [Sources and versions](references/sources-and-versions.md) records research from 2026-10-13, not a permanent latest-version promise. Do not use documentation snapshots as dependency pins.
4. Establish the acceptance path: actor, input, state transition, visible result, denial cases, and evidence. Skill activation does not authorize deployment, destructive data changes, messaging, or publication.

## Route by work

| Work | Read |
|---|---|
| New project / first runnable slice | [Getting started](references/getting-started.md) |
| Ready-to-run fullstack/API/hybrid starter | [Bundled boilerplate](references/boilerplate.md) and [template README](assets/boilerplate/README.md) |
| Folder layout, module boundaries, imports, code conventions | [Folder and code structure](references/folder-and-code-structure.md) |
| Models, ORM, migrations, domain logic, transactions, code organization | [Architecture and code](references/architecture-and-code.md) |
| Templates, forms, HTMX, server-rendered workflows | [Fullstack](references/fullstack.md) |
| DRF endpoints, serializers, auth, pagination, OpenAPI | [REST API](references/rest-api.md) |
| Any admin, inline, dashboard, action, custom page | [Unfold admin](references/unfold-admin.md), [complete feature map](references/unfold-feature-map.md), and [components](references/unfold-components.md); also use `django-unfold-admin` when available |
| UI, tokens, components, responsive/accessibility behavior | [Design system](references/design-system.md) |
| Static/media, runtime settings, queues, testing/deployment | [Production and verification](references/production-and-verification.md) |
| Regression tests, permissions/CSRF, concurrency and trust boundaries | [Testing and security](references/testing-and-security.md) |
| Unfold third-party packages, import/export, revisions, object grants | [Unfold integrations](references/unfold-integrations.md) |
| Dependency selection or integration | [Packages](references/packages.md) |
| Package updates, Django upgrades, lockfiles, release rollout | [Package updates](references/package-updates.md) |
| End-to-end implementation example | [Vertical slice](references/vertical-slice.md) |
| Official documentation and version policy | [Sources](references/sources-and-versions.md) |

Read only relevant references. The Unfold guide is self-contained if the separate admin skill is unavailable.

## Delivery workflow

For a new application, read getting-started, folder structure, and architecture before coding. Choose fullstack/API/hybrid and document the required surfaces and database/auth boundaries. Build one connected vertical slice (model, migration, validation, permissions, adapter, Unfold registration, visible result) before expanding horizontally.

When the bundled starter fits a new project, generate it with `scripts/create_project.py` into a new directory, then follow its README. Do not overwrite an existing checkout or present the sample Project domain as the user's completed product. Extend it toward the user's actual acceptance criteria.

For existing applications, trace the current caller-to-database path and preserve conventions. Put domain rules where every affected entrypoint can invoke them. Deliver a real result on the requested user path; do not stop with a scaffold, a schema, or a design document when implementation was requested.

For a broad admin task, use the feature map to consider every relevant family, but select features by user need. The guides cover all topics in the current official navigation, not a requirement to enable everything. Follow the installed API, and report unavailable/deprecated behavior explicitly.

For upgrades, read package-updates first, capture the current baseline, update a coherent dependency group, validate affected contracts, and preserve a recovery path.

## Implementation invariants

- Prefer ordinary Django apps and ORM. Add services for shared multi-step workflows, QuerySet methods for reusable reads, async/queues for actual requirements. Avoid generic repositories around the ORM and scaffolding without callers.
- Enforce server-side authorization consistently across HTML, API, admin, exports, related-object choices, and tasks. A hidden menu or `IsAuthenticated` alone does not enforce ownership/tenant isolation.
- Declare writable form/serializer fields explicitly. Assign owner, tenant, and privileged state from trusted context. Validate related objects in the same scope.
- Enforce durable invariants with database constraints. Model `save()` does not automatically call `full_clean()`; DRF does not automatically run model `clean()`. Define validation deliberately.
- Keep transactions short; protect conflicting writes when needed. Dispatch dependent work after commit; use durable outbox/idempotency when loss or duplication requires it.
- Always use Unfold bases, documented app order, permission-scoped callbacks, named URLs, and version-compatible styling. Preserve existing UI design unless redesign is requested.
- WhiteNoise handles collected static. Uploaded/private media needs separate storage and access checks. Use modern `STORAGES` configuration while preserving other aliases.
- Maintain schema/endpoint agreement and visible loading, empty, invalid, forbidden, and failure states. No dead controls or synthetic data presented as authoritative.

## Verify proportionately

Follow repository/user requirements. Run relevant system checks, migration drift checks, focused existing tests, and a real authenticated path when UI/provider/runtime acceptance requires it. Add regression tests for risky logic, permissions, concurrency, or substantive bugs; avoid tests that only restate low-impact presentation edits.

For admin-only work follow the separate `django-unfold-admin` testing convention when used, unless user/repository instructions require tests. Still inspect actual registration, permissions, and the rendered path.

Report exact verification results and limitations. Schema validation is not authorization proof; a build or health check is not login/submit proof; eager task execution is not worker delivery proof. Finish with what changed and what was verified.
