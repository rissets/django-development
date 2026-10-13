# Sources and version policy

Researched 2026-10-13 (Asia/Jakarta). This is a dated research snapshot. Official versioned docs and installed release notes override older examples; project requirements determine architecture. Use the primary documentation below and the live Unfold feature map. The skill contains implementation guidance rather than a bibliography of internal research materials.

## Version decisions

The official download page lists supported Django 5.2 LTS, 6.0, and 6.1; Django 6.1 release notes list Python 3.12–3.14. Pick a supported series matching the actual dependency ecosystem and project needs, then its supported patch; do not silently upgrade an existing project because the user supplied 6.1 docs. [Downloads](https://www.djangoproject.com/download/), [6.1 release notes](https://docs.djangoproject.com/en/6.1/releases/6.1/)

DRF's current requirements page lists Django 5.2/6.0/6.1, but the compatible Python range for an application is the intersection of Python, Django, and all selected packages. The Python range in one package does not override Django's range. [DRF requirements](https://www.django-rest-framework.org/)

WhiteNoise's stable page was labeled 6.12.0 at research time. Several other `latest` manuals expose development build identifiers. Treat website labels as documentation metadata, not confirmed installed/PyPI versions or a tested all-package matrix. No runnable application/dependency compatibility matrix was built for this research.

## Upgrade-sensitive items

| Historical pattern | Current decision |
|---|---|
| `django.core.urlresolvers`, `django.conf.urls.url` | Verify modern `django.urls` reverse/path/re_path |
| `ugettext_lazy`, old staticfiles tags | Verify modern translation/static APIs |
| `STATICFILES_STORAGE`, `DEFAULT_FILE_STORAGE` | Modern `STORAGES`; preserve aliases and version compatibility |
| Old DRF `filter_fields`, pagination/view attributes | Current django-filter/DRF contract, not literal old-example port |
| Serializer-only business validation | Shared workflow plus applicable DB constraints and path checks |
| `csrf_exempt` demo / always-JWT browser auth | Explicit client/session/CSRF design |
| Old allauth/crispy setup | Current release settings/middleware/template pack |
| Old Unfold Tailwind 3 configuration | Installed-version guidance; simple custom CSS often sufficient |
| `EMAIL_*` copied into Django 6.1 without review | Verify mailer migration and package compatibility |
| Django Tasks import means background execution | Production queue/backend/worker still required |

## Official source index

Each page was opened during research; routing describes what to verify, not a claim that the entire website was read.

| Topic | Primary source |
|---|---|
| Django user-requested entry | [Official documentation](https://docs.djangoproject.com/en/6.1/) |
| Supported releases | [Official documentation](https://www.djangoproject.com/download/) |
| Release/API changes | [Official documentation](https://docs.djangoproject.com/en/6.1/releases/6.1/) |
| Code design | [Official documentation](https://docs.djangoproject.com/en/6.1/misc/design-philosophies/) |
| ORM performance | [Official documentation](https://docs.djangoproject.com/en/6.1/topics/db/optimization/) |
| QuerySet API | [Official documentation](https://docs.djangoproject.com/en/6.1/ref/models/querysets/) |
| Instance validation | [Official documentation](https://docs.djangoproject.com/en/6.1/ref/models/instances/) |
| Transactions | [Official documentation](https://docs.djangoproject.com/en/6.1/topics/db/transactions/) |
| Migrations | [Official documentation](https://docs.djangoproject.com/en/6.1/topics/migrations/) |
| Custom user | [Official documentation](https://docs.djangoproject.com/en/6.1/topics/auth/customizing/) |
| ModelForms | [Official documentation](https://docs.djangoproject.com/en/6.1/topics/forms/modelforms/) |
| Templates | [Official documentation](https://docs.djangoproject.com/en/6.1/topics/templates/) |
| Async | [Official documentation](https://docs.djangoproject.com/en/6.1/topics/async/) |
| Tasks | [Official documentation](https://docs.djangoproject.com/en/6.1/topics/tasks/) |
| Deployment | [Official documentation](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/) |
| CSP | [Official documentation](https://docs.djangoproject.com/en/6.1/ref/csp/) |
| Testing | [Official documentation](https://docs.djangoproject.com/en/6.1/topics/testing/overview/) |
| DRF requirements | [Official documentation](https://www.django-rest-framework.org/) |
| Requests | [Official documentation](https://www.django-rest-framework.org/api-guide/requests/) |
| Serializers | [Official documentation](https://www.django-rest-framework.org/api-guide/serializers/) |
| Generic views | [Official documentation](https://www.django-rest-framework.org/api-guide/generic-views/) |
| Authentication | [Official documentation](https://www.django-rest-framework.org/api-guide/authentication/) |
| Permissions | [Official documentation](https://www.django-rest-framework.org/api-guide/permissions/) |
| Throttling | [Official documentation](https://www.django-rest-framework.org/api-guide/throttling/) |
| Spectacular overview | [Official documentation](https://drf-spectacular.readthedocs.io/en/latest/) |
| Schema annotations | [Official documentation](https://drf-spectacular.readthedocs.io/en/latest/customization.html) |
| Schema/CSP caveats | [Official documentation](https://drf-spectacular.readthedocs.io/en/latest/faq.html) |
| Unfold setup | [Official documentation](https://unfoldadmin.com/docs/installation/quickstart/) |
| Unfold auth | [Official documentation](https://unfoldadmin.com/docs/installation/auth/) |
| Unfold configuration | [Official documentation](https://unfoldadmin.com/docs/configuration/settings/) |
| Dashboard | [Official documentation](https://unfoldadmin.com/docs/configuration/dashboard/) |
| Custom admin pages | [Official documentation](https://unfoldadmin.com/docs/configuration/custom-pages/) |
| Components | [Official documentation](https://unfoldadmin.com/docs/components/introduction/) |
| Styles compatibility | [Official documentation](https://unfoldadmin.com/docs/styles-scripts/customizing-tailwind/) |
| WhiteNoise overview | [Official documentation](https://whitenoise.readthedocs.io/en/stable/index.html) |
| Static setup | [Official documentation](https://whitenoise.readthedocs.io/en/stable/django.html) |
| Accessibility | [Official documentation](https://www.w3.org/WAI/WCAG22/quickref/) |
| UI patterns | [Official documentation](https://design-system.service.gov.uk/components/) |
| HTMX | [Official documentation](https://htmx.org/docs/) |
| django-htmx | [Official documentation](https://django-htmx.readthedocs.io/en/latest/tips.html) |
| Filter integration | [Official documentation](https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html) |
| Allauth | [Official documentation](https://docs.allauth.org/en/latest/installation/quickstart.html) |
| JWT | [Official documentation](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) |
| CORS | [Official documentation](https://github.com/adamchainz/django-cors-headers) |
| Crispy | [Official documentation](https://django-crispy-forms.readthedocs.io/en/latest/install.html) |
| Environment | [Official documentation](https://django-environ.readthedocs.io/en/latest/quickstart.html) |
| Storage | [Official documentation](https://django-storages.readthedocs.io/en/latest/) |
| Celery | [Official documentation](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html) |
| Channels | [Official documentation](https://channels.readthedocs.io/en/stable/) |
| Redis | [Official documentation](https://github.com/jazzband/django-redis) |
| Guardian | [Official documentation](https://django-guardian.readthedocs.io/en/stable/) |
| History | [Official documentation](https://django-simple-history.readthedocs.io/en/latest/) |
| Import/export | [Official documentation](https://django-import-export.readthedocs.io/en/latest/) |
| pytest-django | [Official documentation](https://pytest-django.readthedocs.io/en/latest/) |
| Debug toolbar | [Official documentation](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html) |
| PostgreSQL driver | [Official documentation](https://www.psycopg.org/psycopg3/docs/basic/install.html) |

## Refresh process

Inspect the current manifest/lock/runtime without dumping credentials. Open only official pages relevant to the task and installed version. Resolve contradictory docs with that release's source/changelog; label unresolved compatibility. For upgrades review removed APIs, schema output, middleware/static, migration effects, and affected permission/browser paths. Offline use should explicitly state reliance on this dated snapshot.

## Implementation and upgrade sources

- [uv projects](https://docs.astral.sh/uv/guides/projects/) and [locking/sync](https://docs.astral.sh/uv/concepts/projects/sync/).
- [Django upgrade procedure](https://docs.djangoproject.com/en/6.1/howto/upgrade-version/).
- [pip-tools](https://pip-tools.readthedocs.io/en/latest/) and [Poetry update](https://python-poetry.org/docs/cli/#update).
- [Complete Unfold navigation map](unfold-feature-map.md): 80 canonical pages rechecked on 2026-10-13, including every current integration topic.

Operational recipes and code examples belong to getting-started, architecture, structure, vertical-slice and Unfold guides; this file remains an official-source/version lookup.
