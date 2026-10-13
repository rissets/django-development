# Memperbarui package dan Django

Gunakan untuk patch, security fix, upgrade framework/package, lock refresh, dan migrasi stack. Upgrade bukan izin deploy production. Panduan ini mendefinisikan perubahan yang dapat direview, kompatibilitas, verifikasi, dan recovery.

## 1. Inventaris sebelum mengubah

Catat Python/Django/DRF/Unfold/spectacular/WhiteNoise dan integration versions; manifest, lock, groups/extras, DB/server, frontend build, CI/container. Gunakan metadata package/version tanpa dumping secrets/settings. Contoh pada uv:

```bash
uv run python -m django --version
uv tree
uv pip list --outdated
```

`uv pip list` menggambarkan environment, bukan perubahan manifest/lock. Jangan menambal environment live lalu menyebutnya release reproducible. Preserve dirty user work dan gunakan checkout/environment yang aman sesuai repository.

## 2. Pilih lingkup

| Update | Fokus |
|---|---|
| Security/patch | Paket terdampak + transitives perlu; minimalkan perubahan unrelated |
| Django minor/major | Semua release notes intermediate, Python/DB minimums, removed/deprecated APIs |
| Unfold | Templates/forms/decorators/options, CSS/Tailwind, auth, third-party MRO |
| DRF + spectacular | Runtime contracts, serializer/permissions, schema/client compatibility |
| DB driver | Wheel/system libpq, connection/pool, actual engine/architecture |
| Queue/cache/storage | Worker interoperability, serialization, credentials/topology, state durability |
| Broad refresh | Hanya jika diminta; kelompokkan perubahan agar failure bisa dilokalisasi |

Default update dalam constraint existing. Mengganti Django series atau Python minimum adalah keputusan eksplisit, bukan akibat tidak sengaja `--upgrade`. Baca support matrix/release notes resmi. Deprecation warnings perlu diperbaiki sebelum pindah ke series yang menghapus API. [Django upgrade guide](https://docs.djangoproject.com/en/6.1/howto/upgrade-version/)

## 3. uv workflow

Targeted lock refresh dalam rentang manifest:

```bash
uv lock --upgrade-package django-unfold
uv sync --locked
```

Group terkait API bila perlu:

```bash
uv lock --upgrade-package djangorestframework --upgrade-package drf-spectacular
uv sync --locked
```

Upgrade rentang Django merupakan manifest change tersendiri, contoh bila series 6.1 telah dipilih kompatibel:

```bash
uv add 'Django>=6.1,<6.2'
uv sync --locked
```

Broad refresh hanya ketika authorized:

```bash
uv lock --upgrade
uv sync --locked
```

`--upgrade` tidak mengabaikan constraint manifest. `--locked` memeriksa lock sinkron; `--frozen` menghindari lock update namun tidak melakukan freshness check yang sama. Untuk CI/deployment pilih kebijakan yang memastikan manifest/lock sinkron, groups produksi eksplisit, dan Python tepat. Commit `pyproject.toml` plus `uv.lock` bersama. [uv locking/sync](https://docs.astral.sh/uv/concepts/projects/sync/)

## 4. Workflow package manager lain

| Existing convention | Lakukan |
|---|---|
| pip-tools | Ubah constraints/input, `pip-compile --upgrade-package PACKAGE` untuk lock terkait, `pip-sync` environment sesuai file hasil |
| Poetry | Targeted `poetry update PACKAGE`; ubah range lewat `poetry add` jika memang dipilih, commit lock |
| Pinned requirements tanpa resolver source | Ubah pin terpilih, resolve dalam clean environment, cek conflicts dan simpan artifact reproducible menurut repo |

Verifikasi syntax terhadap installed CLI; jangan pindahkan manager hanya untuk update sederhana. `pip freeze` environment developer tidak otomatis menjadi dependency policy. Jangan mencampur install manual dengan locked deployment.

Panduan resmi: [pip-tools](https://pip-tools.readthedocs.io/en/latest/) dan [Poetry commands](https://python-poetry.org/docs/cli/#update).

## 5. Periksa diff dan compatibility

Inspect perubahan direct/transitive deps, new extras, marker Python/platform, prerelease/git dependencies, licenses, removed packages, dan container base image. Rilis docs `latest` bisa mendeskripsikan versi belum dirilis; cocokkan changelog/tag/package metadata.

Untuk Django cek models/constraints/migration behavior, auth forms, admin API, middleware, storage settings, email/tasks/CSP, DB versions. Jangan otomatis memakai API baru hanya karena upgrade memungkinkan.

Untuk Unfold cek seluruh registered admin/inline bases, UserAdmin forms, optional apps ordering, custom sites/URL namespaces, action/dialog signatures, dataset context, components/templates, colors/CSS. Tailwind 3/4 bukan perubahan cosmetic jika styles mempengaruhi forms. Integration deprecation bukan alasan uninstall fitur produk tanpa migration plan.

Untuk DRF/spectacular bandingkan generated schema sebelum/sesudah, termasuk request/response fields, enums, nullability, auth, pagination, operationId. Dokumentasikan perubahan client contract dan regenerate client hanya bila repo memang memilikinya. Valid schema bisa tetap breaking untuk konsumen.

## 6. Verifikasi sebelum release

Jalankan baseline sebelumnya dulu jika belum diketahui, lalu checks/tests sesuai scope:

- Import/setup/system checks dan migration drift.
- Existing focused tests dan CI-required suite.
- Permission-negative paths, writable fields, scoped related choices, invalid payloads.
- Schema validation/diff untuk API; authenticated browser flow untuk UI/admin.
- Build CSS/JS lalu collectstatic ke environment staging yang sesuai; fetch hashed assets dengan DEBUG false.
- Worker/backend/storage real smoke bila package tersebut berubah.
- Production settings check dengan konfigurasi tepat; DB migration plan/SQL/locks bila ada.

Tests lama lulus bukan alasan melewatkan flow yang terkena removed API. Jangan menulis test yang hanya memeriksa version string. API-only upgrade dengan admin membutuhkan admin static/auth compatibility juga.

## 7. Rollout dan recovery

Catat release artifact/container digest, previous lock, migration impact, backup/restore kebutuhan, dan monitoring indikator yang konkret. Code rollback tidak otomatis membatalkan data migration; gunakan expand/contract jika kompatibilitas old/new instances penting. Jangan menjalankan `migrate` ke production atau menghapus volumes untuk menyelesaikan conflict tanpa otorisasi dan analisis data.

Sebelum deploy yang authorized, siapkan artefak yang sudah lulus dan reviewable. Setelah deploy verifikasi readiness plus real user path; background failures, logs, asset 404, dan permission regression relevan. Record rollback trigger dan hasil sesuai workflow repo.

## 8. Catatan hasil upgrade

Tuliskan paket old→new yang benar-benar diperoleh, alasan update, compatibility/deprecation fixes, schema/migration effects, commands/results, real-path evidence, dan limit yang belum dibuktikan. Jangan menyebut “semua latest” tanpa metadata terverifikasi atau “aman production” hanya dari resolver success.
