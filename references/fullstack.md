# Fullstack Django

Use for product/public HTML, forms, components, and progressive enhancement. Admin follows [Unfold](unfold-admin.md).

| Need | Approach |
|---|---|
| Content, forms, search, tables, operations | Django templates/forms, normal HTTP first |
| Partial refresh/inline edits/dependent controls | HTMX/django-htmx selectively |
| Small client state | Existing lightweight JS or plain JS |
| Offline/editor/canvas with substantial state | Chosen SPA frontend plus DRF |
| Bidirectional live connections | Assess ASGI/Channels and connection permissions |

HTML/API adapters can call the same domain workflow; HTML does not need loopback REST calls. Do not add DRF just to render a form. Namespace URLs and use `reverse()`/`{% url %}`.

## Forms and templates

Use `Form` for non-model inputs and `ModelForm` for model edits. Explicit writable `Meta.fields`; owner/tenant/privilege remain server-controlled. An overridden form `clean()` calls `super().clean()`. With `save(commit=False)`, save the instance then `save_m2m()` when needed. [ModelForm](https://docs.djangoproject.com/en/6.1/topics/forms/modelforms/)

Bind POST/files, validate server-side, preserve bound values on failure, and use post/redirect/get after ordinary success. GET is safe; unsafe mutations require CSRF. Scope object lookup and selectable relations. Authorize server-side regardless of hidden controls.

Use base templates and app-namespaced includes. Pass bounded display data; keep business calculations out of templates. Preserve autoescape, use `json_script` for embedded JSON, and sanitize rich content deliberately. Do not use `safe`/`mark_safe` for untrusted content. Match template configuration to installed Django. [Templates](https://docs.djangoproject.com/en/6.1/topics/templates/)

For uploads use multipart, size/type policy, safe generated paths, separate media storage, and protected private downloads. Filename/client MIME alone cannot establish content safety.

## HTMX

Define full-page/fragment responses. Send CSRF via `X-CSRFToken` on unsafe requests. Emit `Vary: HX-Request` when response shape depends on it; caching also needs relevant auth/identity dimensions. [django-htmx tips](https://django-htmx.readthedocs.io/en/latest/tips.html)

Do not assume every HTML error status swaps by default. Verify configured validation-status behavior, session-expiry redirects, timeouts, and focus after replacement. Preserve ordinary navigation/form fallback where feasible. Server auth/escaping applies to all fragments. [HTMX](https://htmx.org/docs/)

Disable controls only while pending, restore them on failure, announce progress, and avoid unexpected focus jumps. Keep filter/search/page state in URLs when back/refresh/bookmarks matter. Handle rapid-search races and debounce where useful.

## State and acceptance

Define populated, empty, invalid, pending, success, forbidden, and failed states. Preserve input and actionable errors; empty state offers a real next action. Failed sources must not show fake KPIs. Show period, units, timezone, and provenance for metrics.

Verify the requested actor can log in, list/filter, submit invalid then valid input, follow the resulting detail link, and see persisted state. Confirm denial for unauthorized users. Inspect browser errors/layout for UI scope. Template rendering alone is not browser proof. Apply [design guidance](design-system.md).

## Organisasi views dan URL

Setiap domain mempunyai URL namespace, views sesuai resource/use case, forms, dan template namespaced. Shared layout ada di project templates. `urls.py` project hanya composition; jangan menumpuk semua view/domain di sana. Gunakan names untuk redirects, pagination, sidebar, dan breadcrumbs sehingga deployment prefix tidak mengharuskan mengganti string di banyak template.

List/detail GET bersifat read-only. Create/edit/cancel/archive memakai unsafe method dan CSRF; jangan membuat action mutation melalui anchor GET. Untuk update, load object dari authorized queryset sebelum bind form. Server assignment owner/tenant tidak berasal dari hidden field. Shared workflow mengatur transition yang dipakai API/admin juga.

## Daftar dengan URL state dan pagination

Validasi query dengan Form agar date/enum/page/order tidak diterjemahkan menjadi ORM expression bebas. Terapkan policy dulu, filter kedua, deterministic ordering ketiga, pagination terakhir. Simpan query parameters yang valid pada next/prev links; reset page bila filter berubah. Django Paginator cocok untuk bounded conventional list; keyset/cursor dipilih bila scale/contract membutuhkan.

Contoh core list untuk Project example:

```python
from django.core.paginator import Paginator
from apps.projects.models import Project


def project_page(*, actor, page_number):
    queryset = Project.objects.visible_to(actor).select_related("owner")
    return Paginator(queryset, 25).get_page(page_number)
```

`get_page()` mempunyai fallback behavior untuk invalid page; pilih raise/404 jika kontrak produk membutuhkan. Halaman kosong dan no-match search berbeda: yang pertama dapat menawarkan create, yang kedua clear filters. Jangan memuat seluruh queryset ke list sebelum paginate.

## Render field/error secara deliberate

Django Form widgets mempunyai accessibility hooks; custom renderer harus mempertahankannya. Hubungkan label `for` ke widget ID, hint/error dengan `aria-describedby`, invalid state dengan `aria-invalid`, dan pertahankan submitted value. Formsets membutuhkan management form dan prefix stabil. Jangan memakai custom markup yang menghapus hidden management inputs atau menggandakan ID.

`form.as_div` dapat menjadi baseline sederhana; untuk final design gunakan shared field component sesuai widgets nyata dan version Django. Date/currency formatting harus cocok parsing server; multi-widget perlu label/description yang benar. Non-field errors tampil di tempat yang ditemukan user, bukan hanya logs.

## Formset dan beberapa objek

Gunakan inline formset ketika relasi FK parent-child dan workflow memang edit bersamaan. Parent lookup scoped; formset queryset/related choice scoped; validasi parent dan children sebelum save. Gunakan atomic bila semua perubahan harus commit bersama, dan handle `save_m2m`/deletes dengan lifecycle rules. Rencanakan concurrency/version check jika dua operator dapat menimpa edit.

Multi-step forms diperlukan bila tahap keputusan/data terlalu banyak untuk satu halaman. Define state persistence/session expiry/authorization untuk setiap step; jangan menyimpan secrets/large uploads di cookie session. Jangan menggunakan wizard untuk menutupi business model yang belum jelas.

## Upload dan download

Form upload `enctype="multipart/form-data"`, bind request.FILES, limits di web/proxy/server, extension/content validation yang sesuai, storage naming aman, dan error recovery. Malware scanning/provider processing dipilih sesuai risiko/data; jangan mengklaim file aman dari MIME saja. Private media: authorized lookup dan signed delivery/streaming dengan headers sesuai file; jangan memasukkan private media ke WhiteNoise/static directory.

## HTMX wiring dan cache

Tempatkan CSRF header pada ancestor yang relevan; render token sesuai Django, jangan mengambil cookie HttpOnly dari JS. `HX-Request` bukan autentikasi dan dapat dipalsukan. Cache harus membedakan full page/fragment dan identity/scope. Fragment tidak boleh mengirim entire application shell ke target kecil.

Konfigurasi status/response-handling untuk errors sebelum memakai 422/400 fragment. HTMX redirects/refresh headers, trigger events, swap target dan URL history dipilih sesuai flow. Batalkan/debounce rapid search; stale response tidak boleh mengganti query terbaru. Session-expiry response harus kembali ke login yang jelas dan menjaga safe return URL.

## Account journeys

Pilih built-in Django auth atau allauth berdasarkan requirements (registration, verification, social/MFA/headless). Login, logout, password reset/change, account status, rate limits, email delivery, and redirects harus lengkap jika diminta. Logout mengikuti HTTP method yang didukung installed Django, bukan link GET lama. `next` destination harus safe same-host policy, bukan arbitrary URL dari input.

Browser session tests memeriksa CSRF/expiry/denied state; mock email hanya memverifikasi application logic. Provider-backed account verification memerlukan real delivery evidence bila itu acceptance path.

## Content, locale, dan halaman sistem

Gunakan i18n untuk user-facing strings bila multilingual dibutuhkan, locale-aware dates/numbers, timezone conversion, dan text expansion pada responsive layout. SEO/sitemap/feeds hanya bila produk publik memerlukannya. Custom 400/403/404/500 templates tidak membocorkan exception/private details dan harus diuji dengan DEBUG false; DEBUG error page bukan final product UX.
