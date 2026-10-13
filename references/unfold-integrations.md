# Integrasi paket pada Django Unfold

Ini panduan seluruh 14 integration topics pada navigasi resmi saat 2026-10-13. Setup Unfold tidak menggantikan konfigurasi package utama. Install hanya untuk kebutuhan produk; cek release/lock dan permissions sebelum menyalin MRO/imports. Daftar fitur lengkap: [feature map](unfold-feature-map.md).

## Urutan dan inheritance

Template override apps Unfold ditempatkan sebelum package yang dioverride. Tidak semua integrasi memakai contrib app; beberapa memakai forms/widget atau re-registration. Django hanya mengizinkan satu registered ModelAdmin per model per site; unregister deliberate saat mengganti admin bawaan dan preserve behavior/forms yang masih dipakai.

| Integration | Wiring Unfold | Use case dan verifikasi |
|---|---|---|
| django-celery-beat | Re-register schedule/task admins dengan Unfold-compatible classes | Scheduler configuration permissions, timezone/schedule, singleton scheduler dan real task execution |
| django-reversion | `unfold.contrib.reversion` sebelum `reversion`; setup revisions paket utama | Revision capture, recover/revert rights, relations dan consequences restore |
| djangoql | Mix search integration pada admin yang cocok | Scope/search_fields/expensive query policy; custom standalone pages belum otomatis styled |
| django-money | MoneyField widgets supported; tanpa contrib app tambahan pada docs | Currency/rounding, localized input, migration dan serializers yang kompatibel |
| django-constance | `unfold.contrib.constance` sebelum `constance`, documented widgets/extra fields | Runtime configuration rights, value validation, secrets tidak ditampilkan sembarangan |
| django-json-widget | Styled/dark support setelah package terpasang | Editor payload size, JSON validation, readonly/write permission |
| django-waffle | Re-register admins; documented Unfold FlagAdmin untuk user selection | Flag targeting, assignment permission, cached flag effects, default behavior |
| django-import-export | `unfold.contrib.import_export`, Unfold ImportForm/ExportForm | Field allowlist, tenant-aware import/export, dry-run, size limits dan audit |
| django-reversion-compare | Contrib compare sebelum package; membutuhkan reversion | Diff display fields/relations/permissions dan revision source correctness |
| django-simple-history | Contrib sebelum `simple_history`; SimpleHistoryAdmin + ModelAdmin | History capture/actor, bulk/worker gaps, read/revert access, retention |
| django-guardian | `unfold.contrib.guardian` template override plus guardian setup/backend | Object grants UI; scope lists/actions/suggestions secara terpisah |
| django-modeltranslation | Version-specific integration; documented deprecation sejak Unfold 0.102.0 | Confirm supported path before adoption; language data and forms/migrations preserved |
| django-hijack | `unfold.contrib.hijack` for notice/buttons + package authorization | Explicit impersonation grant, audit, exit control dan state outside admin |
| django-location-field | `unfold.contrib.location_field` sebelum `location_field`, location widget/form | Provider/geospatial representation, validation, privacy dan collected assets |

Baca canonical integration pages melalui [feature map](unfold-feature-map.md#integrations); exact app names/backend forms/deprecation mengikuti installed release. Minimal mixin pattern tidak membuktikan seluruh behavior terintegrasi.

## Import/export yang scoped

Resource declaration mengatur fields/order/widgets/import identity; admin mengatur permissions, scope, forms, dan UX. Export mengambil authorized queryset dan hanya field yang boleh dilihat. Import memvalidasi target tenant/owner dan related references, termasuk existing records identified by business key. Jangan memperbolehkan CSV menetapkan `is_superuser`, tenant arbitrary, atau status workflow privileged.

```python
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ImportForm, ExportForm


class ScopedImportExportAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
```

Ini base pattern yang belum diregistrasikan; domain admin menambahkan Resource class dan authorization. Pakai MRO yang compatible dengan versi terpasang. django-import-export 4.x+ berbeda dari contoh ExportActionModelAdmin Unfold lama; jangan mengimpor class yang sudah tidak dibutuhkan/tersedia. [Official integration](https://unfoldadmin.com/docs/integrations/django-import-export/)

Dry-run dan confirm harus memakai identitas/scope yang sama; storage temporary import files aman dan cleanup jelas. Batch besar bisa membutuhkan async job, bukan request timeout. Transaction behavior tergantung import configuration; tampilkan partial/all-or-nothing result secara benar. Formula-like spreadsheet payload/export merupakan boundary yang perlu kebijakan format consumer sesuai requirements.

## History, revisions, dan audit

History model merekam snapshot/perubahan; reversion membuat revision groups/recovery; compliance audit mungkin membutuhkan immutable event log lain. Tentukan source of truth dan apa yang di-revert: scalar values, foreign keys, inlines, uploaded files, dan external provider state tidak otomatis semuanya kembali.

```python
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin


class TrackedAdmin(SimpleHistoryAdmin, ModelAdmin):
    pass
```

Model tracking/middleware/actor attribution tetap diatur package utama. Uji direct save, bulk update, tasks, imports dan restore path yang dipakai. Viewer/revert permissions berbeda; jangan memberikan recovery privilege hanya karena dapat melihat history. Retention bisa meliputi PII dalam snapshots. [Official history integration](https://unfoldadmin.com/docs/integrations/django-simple-history/)

## Feature flags dan runtime configuration

Flag/config editor perlu domain/schema validation, least privilege, audit, staged rollout, default behavior, dan cache invalidation. Pisahkan public-safe values dari secrets. Scheduler/flags tidak boleh menjadi cara arbitrary code execution melalui field staff tanpa policy. Model permissions melindungi panel; effect policy melindungi tindakan downstream.

## Object grants dan impersonation

Guardian grants tidak membuat seluruh API/admin queryset otomatis scoped. Model-level permission, object grant, ownership/tenant, list scope, autocomplete, exports, and actions harus konsisten. Impersonation merupakan tindakan privileged yang eksplisit; target constraints, actor attribution, session transitions, CSRF, exit UX, dan audit diuji. Styled notice saja tidak membuktikan user telah kembali ke identitas awal.

## Integrasi fields

Money/JSON/location/translation membutuhkan parsing/representation konsisten pada ModelForm, DRF serializers, admin widgets, imports dan migrations. Browser editor bukan backend validator. JSON schema callback tidak mempunyai request context; jangan membuat per-user schema security dari callback global. Rich text membutuhkan sanitization; WYSIWYG tidak membuat HTML trusted.

## Saat compatibility gagal

Trace registered class MRO, app template order, form/widget classes, package changelog, static assets, migration/runtime dependencies. Pilih documented compatible recipe atau implement local adaptation yang kecil dengan evidence. Jangan melemahkan permissions atau mengganti seluruh admin theme supaya sebuah widget tampak bekerja. Laporkan unsupported/deprecated capability dan path migrasi yang konkret.
