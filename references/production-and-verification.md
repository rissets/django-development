# Production and verification

Use for settings, static/media, workers, deployment, and evidence. Deployment remains bounded by the user's authorization.

## Settings and runtime

Keep the repository's settings layout. Separate environment-specific values and parse booleans/lists correctly; `bool("False")` is true. Production should fail clearly if required secrets/hosts/database settings are missing. Use secret injection and commit only sanitized example variable names. Avoid multiple competing env readers. django-environ offers typed parsing and database URLs. [Quickstart](https://django-environ.readthedocs.io/en/latest/quickstart.html)

Check production `DEBUG`, secret handling, `ALLOWED_HOSTS`, HTTPS/cookie settings, CSRF origins, proxy trust, logging, and error behavior. Set `SECURE_PROXY_SSL_HEADER` only for a proxy that reliably strips/sets the header. Roll out HSTS with the actual HTTPS/domain topology. These values must be verified against the live environment, not blindly pasted. [Deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)

Django 6.x includes CSP support; configure report-only/enforcement and nonce-compatible templates for actual scripts/third parties where required. Do not disable security globally to make docs/charts load. [CSP](https://docs.djangoproject.com/en/6.1/ref/csp/)

## WhiteNoise: static only

WhiteNoise middleware goes immediately after `SecurityMiddleware`. Use `STATIC_ROOT`, collected assets, and `STORAGES["staticfiles"]` with the compressed manifest backend for modern Django. Preserve `default` media and all other storage aliases. Build CSS/JS before collecting. [WhiteNoise Django](https://whitenoise.readthedocs.io/en/stable/django.html)

Illustrative local media plus collected static configuration; adapt paths/backend to the project:

```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

WhiteNoise does not serve uploaded media as its intended use. Private media needs authenticated delivery or appropriately authorized signed URLs/object storage; local production media needs persistence. Hashed static files can have long caching; private data cannot. Brotli requires the optional dependency and actual client/proxy negotiation. Do not suppress manifest errors to conceal missing assets. [WhiteNoise overview](https://whitenoise.readthedocs.io/en/stable/index.html)

Verify actual admin/frontend CSS/JS URLs under `DEBUG=False` through the chosen WSGI/ASGI/proxy/CDN topology. Middleware being configured does not by itself prove correct serving. Object-storage media uses provider-specific django-storages configuration and credentials. [Storage backends](https://django-storages.readthedocs.io/en/latest/)

## Jobs, resources, observability

Use the established WSGI/ASGI server; `runserver` is not production deployment. Budget web concurrency, DB pool, task concurrency, external timeouts, and retries together. Keep health/readiness cheap and separate from full external-provider proof. Record useful request/job identifiers and structured errors without tokens/passwords/private payloads.

Celery workers need a broker and a real running consumer. Schedule only one intended scheduler where required. Use `on_commit()` or supported `delay_on_commit()` to avoid pre-commit reads; the latter does not return a task ID. Eager mode tests logic, not broker/worker delivery. Bound retries and make repeated execution safe. [Celery Django integration](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)

Django Tasks built-in backends are for development/testing; production requires a real execution backend/worker. Queue acceptance requires an enqueued job, consumer execution, result/failure evidence, and a user-visible state when in scope. [Tasks](https://docs.djangoproject.com/en/6.1/topics/tasks/)

## Select verification by failure mode

| Change | Useful evidence |
|---|---|
| Domain/state logic | Boundary cases, database constraints, rollback, concurrency/idempotency where needed |
| Permission/tenant logic | Two actors/tenants, list/detail/create/update/export, unauthorized FK/action |
| HTML/forms | Invalid/valid submissions, persisted result, CSRF and session behavior |
| DRF | APIClient allowed/denied paths, payload exposure, pagination and schema contract |
| Unfold | Registered models, role menu/direct URLs, changeform/actions, actual CSS/JS |
| Static/deployment | Build then collect, production-like asset fetch, proxy/security behavior |
| Worker/provider | Real delivery/execution and failure/retry path, not health only |
| DB-specific behavior | Production engine, actual locks/features; not SQLite equivalence |

Use the project's runner (`manage.py test` or pytest-django) rather than replacing it. Django tests use isolated databases; never target live production for destructive tests. For commit callbacks use callback capture or suitable transaction tests. Permission tests should include restricted users rather than only superusers. [Django testing](https://docs.djangoproject.com/en/6.1/topics/testing/overview/), [pytest-django](https://pytest-django.readthedocs.io/en/latest/)

Examples of checks, adapted to the existing runtime/settings/DB:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py check --deploy --settings=config.settings.production
python manage.py spectacular --file /tmp/application-schema.yaml --validate
```

Do not run a spectacular command in a project without that package, invent a settings module, or run production-configured commands blindly. `collectstatic`/migrations are deployment operations with storage/DB effects: prepare and execute only within the task's authorized environment. Focused checks should cover the change; broaden only for unresolved risk or required CI.

Finish with implemented files/behavior, commands/results, real-path evidence, and exact limits. Mark structural-only or mock/eager checks honestly; do not infer authenticated/public/provider success from health or schema output.
