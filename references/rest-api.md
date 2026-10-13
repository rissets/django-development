# DRF and OpenAPI

Use for JSON APIs; adapt to installed DRF/spectacular versions.

## Contract and implementation

Specify resources, actors, methods, fields, pagination, filtering, errors, and state transitions. Preserve existing envelopes/versioning. Use `201` create, `200` read/update, `204` no-body deletion, `400` invalid input, `403` denied, `404` absent/invisible, `415` unsupported media where appropriate. Unauthenticated denial may be `401` or `403` depending on the first authenticator; test the chosen scheme.

Use `request.data` for parsed JSON/form/multipart bodies (including PUT/PATCH), `request.query_params` for URL params, and explicit parsers for actual media. Retain normal malformed-input/media errors. [Requests](https://www.django-rest-framework.org/api-guide/requests/)

Generic views/viewsets fit normal resources; `APIView`/actions fit explicit workflows. Optimize `get_queryset()` for serializer relations; avoid per-row query methods. [Generic views](https://www.django-rest-framework.org/api-guide/generic-views/)

Explicit serializer fields; split read/write contracts where needed. Validate via `is_valid(raise_exception=True)` and consume `validated_data`. Assign trusted owner/tenant/state on the server. Scope relation-field querysets, including cross-tenant checks. Define PATCH/null/nested-write behavior. DRF does not automatically implement complex nested writes or call model `clean()`. Translate recognized shared-domain errors at the HTTP adapter. [Serializers](https://www.django-rest-framework.org/api-guide/serializers/)

## Access control

Session auth fits same-origin browser APIs; login must be CSRF-protected, authenticated unsafe requests send a CSRF token. Select token/JWT/OAuth only for actual clients/SSO, with HTTPS, expiry/refresh/revocation/storage policy. Cookie-carried bearer tokens still need a CSRF threat model. [Authentication](https://www.django-rest-framework.org/api-guide/authentication/)

Private APIs may default to `IsAuthenticated`, with deliberate public exceptions. This alone is not ownership/tenant authorization. Lists do not automatically check object permissions per row; create has no object to check. Scope querysets and creation rights; custom `get_object()` must call object checks. Exports, aggregates, and actions share scope. [Permissions](https://www.django-rest-framework.org/api-guide/permissions/)

Allowlist cross-origin clients and credentials only as needed. CORS and CSRF are separate; CORS does not authorize server-to-server requests.

## Bounded and reliable operations

Use bounded page sizes and deterministic ordering/tie-breaker. Choose cursor pagination for suitable large feeds, with its ordering constraints. Allowlist filters/order/search and apply after access scoping; django-filter integrates through its DRF backend. [django-filter](https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html)

Move expensive exports/imports to jobs when warranted. For retryable effects define actor-scoped idempotency, fingerprint, and persisted result/constraint where required. Validate webhook signatures/replay before processing.

DRF throttles express approximate usage policy and can race through non-atomic cache operations; they are not hard quotas or complete brute-force/DoS protection. Use gateway/auth controls for those needs. [Throttling](https://www.django-rest-framework.org/api-guide/throttling/)

## drf-spectacular

Add `drf_spectacular`, preserve other DRF settings, set `DEFAULT_SCHEMA_CLASS`. Supply queryset/serializer information; annotate custom requests/responses/parameters/errors with `extend_schema`, fields with `extend_schema_field`, and third-party code with extensions. [Customization](https://drf-spectacular.readthedocs.io/en/latest/customization.html)

Illustrative private session API settings (merge, do not replace unrelated options):

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Application API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
}
```

Register `SpectacularAPIView`, `SpectacularSwaggerView`, optionally Redoc with real named URLs. Title/version/page size/docs visibility are project decisions. Protect internal schema/docs and confirm their auth policy. Pin spectacular and inspect schema diffs when upgrading. [Overview](https://drf-spectacular.readthedocs.io/en/latest/)

Guard schema-only queryset evaluation (e.g. `swagger_fake_view`) with appropriately typed empty querysets rather than weakening runtime scope. Under strict CSP, docs UIs may need sidecar assets and specific CSP adjustments; sidecar alone does not resolve all inline scripts. [FAQ](https://drf-spectacular.readthedocs.io/en/latest/faq.html)

```bash
python manage.py spectacular --file /tmp/application-schema.yaml --validate
```

Review warnings; use `--fail-on-warn` if supported/configured. Structural schema validation is not runtime proof. Test allowed/denied endpoints, field exposure, relation rejection, invalid input, pagination, and documented responses.

## Project URL composition

Contoh untuk vertical slice: router dengan basename eksplisit, schema/docs names stabil, admin route terpisah. Mount pada existing urlpatterns, bukan overwrite semua routes.

```python
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.projects.api.views import ProjectViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("projects/", include("apps.projects.urls")),
    path("api/v1/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="api-docs"),
]
```

`v1` di sini contoh API path; jangan membuat version baru untuk semua perubahan non-breaking. Pada API-only project hapus HTML mounts yang memang tidak dipakai. Internal docs permission/auth berasal dari deliberate spectacular settings; browser docs harus mempunyai cara autentikasi yang sesuai endpoint.

## Annotation untuk operation workflow

`activate` tidak menerima writable Project payload. Annotate custom method dengan contract request kosong dan response Project, bukan membiarkan schema mengiklankan nama/status writable pada operation ini.

```python
from drf_spectacular.utils import extend_schema
from apps.projects.api.serializers import ProjectSerializer

activation_schema = extend_schema(
    request=None,
    responses={200: ProjectSerializer},
    description="Aktifkan proyek draft pada scope actor yang berhak.",
)
```

Apply sebagai decorator method/action sesuai installed spectacular/DRF order. Tambahkan serializer/error response untuk failure states jika kontrak memang mendokumentasikannya; jangan mencantumkan success-only sebagai dokumentasi lengkap. `OpenApiParameter`, examples, enums, extensions dan field annotation digunakan untuk contract yang inference tidak dapat ketahui. Schema generation jangan melakukan authenticated provider calls atau memodifikasi state.

## Serializer layout dan output exposure

List serializer ringkas berbeda dari detail yang membutuhkan related data; writable serializer berbeda jika create/update membawa input lain. Pilih `get_serializer_class()` berdasarkan action dengan schema annotation yang cocok. Limit nested depth dan payload size; pakai explicit fields dan optimized relations. `SerializerMethodField` tidak seharusnya query per object.

Hidden/read-only fields memastikan body tidak mengendalikan owner/tenant/role; service tetap memeriksa permissions untuk caller lain. Jangan mengembalikan raw internal provider payload, tokens, private attachments, atau fields dari `__all__` yang dapat bertambah tanpa review. Related hyperlink harus URL real dan scoped detail endpoint.

## Error policy dan custom exception handling

Preserve DRF default errors kecuali produk mempunyai documented envelope. Untuk custom handler, delegate `rest_framework.views.exception_handler` terlebih dahulu, map recognized domain errors, dan pertahankan HTTP status/headers seperti auth challenge atau Retry-After. Unknown exceptions tidak menjadi 200/success atau generic client validation tanpa logging.

Field-level errors menyebut field/code yang dapat diolah client. Business conflict perlu policy yang konsisten (misalnya 409 bila ditetapkan kontrak). Jangan catch semua exception untuk menghasilkan 400; hal itu menyembunyikan bug dan retry semantics. Request IDs/error tracking tidak boleh memasukkan secret/PII yang tidak diperlukan.

## Auth scenarios

| Client | Pilihan awal | Hal yang diverifikasi |
|---|---|---|
| Same-origin HTML/JS | SessionAuthentication | CSRF-protected login, unsafe methods, cookies/expiry |
| Separate-origin browser | Deliberate session/CORS atau bearer architecture | Trusted origins, credentials, CSRF/cookie/storage policy |
| Mobile/CLI | Token/JWT/OAuth sesuai auth authority | HTTPS, expiry/refresh/revocation, least privilege |
| Third-party integration | OAuth/client auth/API-key policy sesuai kebutuhan | Scopes, rotation, audit, rate limits, no browser secret |

Do not make every anonymous endpoint protected merely because default is private: explicitly mark legitimate health/public/account paths while retaining input/security controls. JWT package selection is not complete identity architecture; delegated SSO uses established identity provider contracts.

## API acceptance matrix

Per operation: valid/invalid body, unsupported media, missing/expired identity, valid identity wrong role/tenant, related ID outside scope, absent object, concurrency/conflict, pagination/order, response fields, and error shape. Compare schema examples against actual result. Upload/export/webhook paths add size/content/provider signature/replay cases. Client-generated tests are useful but do not replace runtime server auth tests.
