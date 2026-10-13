# Django Starter

Boilerplate runnable untuk fullstack, REST API, atau hybrid. Admin selalu Django Unfold. Contoh domain proyek menunjukkan ownership, validation, shared workflows, status transition, HTML/API adapters, dan admin operations dengan data sungguhan dari database lokal.

## Mulai dari skill

Generator membuat folder baru, memperbarui nama manifest/lock dan menghasilkan secret lokal privat. Folder existing ditolak.

```bash
python3 ~/.codex/skills/django-development/scripts/create_project.py /absolute/path/my-app --name my-app --mode hybrid
cd /absolute/path/my-app
uv sync --locked
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Jika Anda menyalin template langsung, jalankan `python3 scripts/init_env.py --mode hybrid` dahulu. Script menolak `.env` existing. Jangan menyalin secret lokal ke production.

Buka [aplikasi lokal](http://127.0.0.1:8000/) dan [admin](http://127.0.0.1:8000/admin/). Buat user biasa melalui admin; tidak ada akun/password demo yang ditanam ke source. Untuk operator, set staff dan beri permissions Project yang diperlukan. Pengelolaan User/Group tetap superuser-only.

## Mode

| APP_MODE | Public HTML | API/docs | Unfold |
|---|---|---|---|
| fullstack | Aktif | Tidak diregistrasikan | Aktif |
| api | Tidak diregistrasikan | Aktif | Aktif |
| hybrid | Aktif | Aktif | Aktif |

Ganti mode di `.env`, restart proses, dan verifikasi surfaces. Satu lock menyertakan library untuk ketiga mode; fullstack menonaktifkan API apps/routes. Generator tidak menghapus file domain sehingga pergantian mode tidak membutuhkan model/migration lain.

## Jalur yang tersedia

- `/accounts/login/`, logout POST, password change/reset: fullstack/hybrid.
- `/projects/`: scoped search, status filter dan pagination.
- `/projects/new/`, detail, edit, activate/archive POST: owner atau global superuser.
- `/api/v1/projects/`: list/create/retrieve/update; activate/archive actions POST. Identity session + CSRF untuk unsafe requests. Owner/status tidak writable dari payload.
- `/api-auth/login/`: credential login untuk session API.
- `/api/schema/`, `/api/docs/`: staff-only; Swagger memakai bundled sidecar assets.
- `/admin/`: scoped dashboard counts, trend tujuh hari, bounded recent records dan real drill-down links.
- `/admin/projects/project/summary/`: protected custom Unfold page.
- Project admin: create/edit via shared services, filters, labels, bulk activation (maksimal 100, partial success), confirmation dialog action.
- `/health/`: process liveness tanpa DB/provider check; bukan bukti seluruh aplikasi siap.

Lifecycle baseline: draft → active → archived, atau draft → archived. Aktivasi berulang idempotent; archive tidak dapat diaktifkan kembali. Hard delete sengaja belum menjadi business capability. Tambahkan policy/operation/UI/tests jika produk membutuhkannya. Tidak ada data synthetic yang otomatis di-seed.

## Commands pengembangan

```bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py test --settings=config.settings.test
uv run python manage.py spectacular --settings=config.settings.test --file /tmp/schema.yaml --validate --fail-on-warn
```

Schema command hanya untuk mode API/hybrid. Test settings menggunakan database terisolasi dan fast password hasher khusus tests. PostgreSQL test dapat dijalankan dengan `TEST_DATABASE_URL` ke database development/test yang actor DB-nya dapat membuat test DB; jangan menunjuk production.

```bash
TEST_DATABASE_URL=postgres://app:local-test-password@127.0.0.1:5432/app uv run python manage.py test --settings=config.settings.test
```

Row-lock test berjalan pada PostgreSQL dan skip pada SQLite. HTML/API tests mencakup credential login/CSRF, ownership, invalid input, state changes, pagination; admin tests mencakup role scope, create/edit/bulk/dialog/custom page dan identity management boundary. CI matrix menjalankan ketiga modes dan PostgreSQL.

## Arsitektur dan pengembangan

Baca [ARCHITECTURE.md](ARCHITECTURE.md) dan [DESIGN.md](DESIGN.md). `apps/accounts` berisi identity; `apps/projects` berisi domain, QuerySet scope, services, forms/views, API, admin, migrations dan tests. `config/settings` membedakan local/test/production. Public static CSS scoped; Unfold mempunyai style system sendiri.

Baseline single-owner, bukan multi-tenant. Tenant/membership, JWT/SSO, Celery, Channels, import/export/history/media upload belum diaktifkan; panduan skill menjelaskan cara menambahnya sesuai requirement. Jangan menyatakan tenant isolation hanya dari ownership sample.

## Production dan Docker

Production settings mewajibkan secret kuat, explicit hosts, PostgreSQL dan DEBUG false. HTTPS/secure cookies aktif; trusted forwarded header hanya bila `TRUST_PROXY=True` dan proxy benar-benar menyaring header klien. Host `.env.production` tidak masuk image.

Isi `.env.production` berdasarkan `.env.production.example`, dengan credential/secret unik dari secret manager. Untuk Compose, `DATABASE_URL` memakai host service `db` dan password APP_DATABASE_PASSWORD. POSTGRES_PASSWORD hanya untuk bootstrap administrator PostgreSQL; app adalah role non-superuser pemilik database aplikasinya. Init script hanya berjalan ketika volume database baru dibuat. Pisahkan migrator/runtime lebih jauh jika produk membutuhkan least-privilege tanpa DDL; URL-encode karakter khusus. Configure sender/SMTP untuk password reset; default localhost SMTP bukan layanan email yang telah diverifikasi.

```bash
docker compose --env-file .env.production config --quiet
docker compose --env-file .env.production build
docker compose --env-file .env.production up -d db
docker compose --env-file .env.production run --rm web python manage.py migrate --noinput
docker compose --env-file .env.production run --rm web python manage.py createsuperuser
docker compose --env-file .env.production run --rm web python manage.py check --deploy
docker compose --env-file .env.production up -d web
```

Default HSTS hanya domain utama dengan rollout awal 3600 detik. `check --deploy` dapat menampilkan W005/W021 karena subdomains/preload sengaja opt-in. Aktifkan hanya setelah seluruh domain terkait siap HTTPS, bukan sekadar untuk menghilangkan warning.

Commands di atas mengubah database/layanan yang dipilih; jalankan pada environment yang diotorisasi. Migrasi sengaja bukan otomatis pada setiap worker/container startup. Image membangun static manifest tanpa runtime secret dan menjalankan Gunicorn sebagai non-root. Host port bind ke loopback; publikasi memerlukan HTTPS reverse proxy/deployment Anda. Health endpoint dikecualikan dari SSL redirect untuk container probe, tanpa membuka authenticated data.

Tidak ada upload UI atau public media route; private media butuh storage dan akses terpisah sebelum ditambahkan. Backups/restore, monitoring, cache/worker services dan concurrency budget mengikuti produk. Jangan menghapus volume untuk mengatasi migration failure.

## Update paket

Preserve manifest constraints dan lock, baca changelog/release compatibility, lalu:

```bash
uv lock --upgrade-package django-unfold
uv sync --locked
```

Lakukan checks/tests, schema diff, admin/browser/static path; update grouping/series dan rollout mengikuti `references/package-updates.md` pada skill. Pin ranges ini starter compatibility policy, bukan janji selalu terbaru. Baseline diverifikasi di review/evidence workspace sumber; lakukan checks kembali pada environment proyek Anda.
