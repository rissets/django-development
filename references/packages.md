# Package selection

Research date: 2026-10-13. Select by actual need, release support, Python/Django/DB compatibility, migration cost, operational dependencies, license, and maintenance. Links below are primary maintainer docs/repositories reviewed for this skill; `latest` may document unreleased code. Recheck exact release/lock before adoption.

## Baseline by mode

| Mode | Starting point |
|---|---|
| Fullstack | Django, required Unfold admin, forms/templates; WhiteNoise if app serves static |
| REST API | Django, DRF, drf-spectacular, required Unfold if admin exists; static for admin/docs |
| Hybrid | Same domain and scoped policies, HTML/forms and DRF adapters |

PostgreSQL/psycopg is a strong default for production relational apps; retain an existing suitable engine. SQLite fits small/local workloads but does not prove PostgreSQL features. Preserve the lock mechanism; do not install every optional package or mix uv/pip/Poetry conventions unnecessarily.

## Core

| Package | When useful | Integration caution | Source |
|---|---|---|---|
| Django | Application core | Match supported series/patch, Python and DB | [Docs](https://docs.djangoproject.com/en/6.1/) |
| djangorestframework | JSON APIs | Auth/permissions, writable fields, list scope explicit | [DRF](https://www.django-rest-framework.org/) |
| django-unfold | Required admin standard | App order, model/inline bases, auth integration | [Quickstart](https://unfoldadmin.com/docs/installation/quickstart/) |
| whitenoise | App-served collected static | Modern storage config; not media | [Django integration](https://whitenoise.readthedocs.io/en/stable/django.html) |
| drf-spectacular | DRF OpenAPI/schema/docs | Pin and review schema diffs; annotate custom paths | [Docs](https://drf-spectacular.readthedocs.io/en/latest/) |
| psycopg | PostgreSQL driver | `psycopg`, not `psycopg3`; choose binary/C/pool extras for runtime | [Install](https://www.psycopg.org/psycopg3/docs/basic/install.html) |

## Add only for a concrete feature

| Package | Trigger | Boundary/caution | Source |
|---|---|---|---|
| django-filter | Typed API filters | DRF backend; allowlist and scope first | [Integration](https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html) |
| django-allauth | Account verification/social login/MFA/headless auth | Inspect current middleware/backends/settings; don't paste 2019 config | [Quickstart](https://docs.allauth.org/en/latest/installation/quickstart.html) |
| djangorestframework-simplejwt | Bearer JWT clients | Expiry/refresh/revocation/storage design; not automatic browser default | [Docs](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) |
| django-cors-headers | Browser cross-origin API | Explicit origins; middleware order; CORS separate from CSRF | [Maintainer repo](https://github.com/adamchainz/django-cors-headers) |
| django-htmx | Server HTML partial interactions | CSRF, Vary headers, failure/focus handling | [Tips](https://django-htmx.readthedocs.io/en/latest/tips.html) |
| django-crispy-forms | Reusable form layout | Since v2, template packs are separate; match UI theme | [Install](https://django-crispy-forms.readthedocs.io/en/latest/install.html) |
| django-environ | Typed environment settings | One parsing approach; no secret defaults in production | [Quickstart](https://django-environ.readthedocs.io/en/latest/quickstart.html) |
| django-storages | Object-storage static/media | Provider config, private/public separation, access policy | [Docs](https://django-storages.readthedocs.io/en/latest/) |
| Celery | Durable background processing/retries/scheduling | Real broker/workers; idempotency; after-commit dispatch | [Django](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html) |
| channels / channels-redis | WebSockets/bidirectional realtime | ASGI, connection/group authorization and deployment | [Docs](https://channels.readthedocs.io/en/stable/) |
| django-redis | Redis cache extras | Assess Django built-in Redis backend first; tenant keys/TTL | [Maintainer repo](https://github.com/jazzband/django-redis) |
| django-guardian | Per-object grants | Does not replace list scoping; verify Unfold integration | [Docs](https://django-guardian.readthedocs.io/en/stable/) |
| django-simple-history | Model change history | Bulk/external write gaps, privacy, actor and retention | [Docs](https://django-simple-history.readthedocs.io/en/latest/) |
| django-import-export | Tabular admin import/export | Scope/fields/access, size limits, Unfold integration | [Docs](https://django-import-export.readthedocs.io/en/latest/) |
| pytest-django | Existing pytest-based tests | Isolated DB; transaction/callback semantics | [Docs](https://pytest-django.readthedocs.io/en/latest/) |
| django-debug-toolbar | Development query profiling | Development-only URLs/middleware; no production exposure | [Install](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html) |

Built-in auth/forms/cache/CSP/tasks may remove a dependency, depending on installed Django. Tasks still needs an execution backend; history is not automatically an immutable compliance audit. Features such as feature flags, money, version rollback, and periodic task admin can use Unfold's documented integrations when requested; do not select packages only because they appear in that catalog.

## Adoption checklist

Record why the package is needed, compatible release, app/middleware order, settings/static/migrations, operational service if any, and actual verification. Dependency resolution alone is not compatibility proof. When updating a project, preserve its data and custom integrations and review release notes rather than replacing the entire stack.
