# Boilerplate yang dibundel

Gunakan [assets/boilerplate/README.md](../assets/boilerplate/README.md) dan kode template pada `assets/boilerplate/` untuk proyek baru. Ini application executable dengan migrations/lock/templates/tests, bukan kumpulan snippets. Untuk existing project, reuse pola/komponen yang relevan tanpa menimpa arsitektur/settings/data.

## Membuat proyek

```bash
python3 ~/.codex/skills/django-development/scripts/create_project.py /absolute/path/my-app --name my-app --mode hybrid
cd /absolute/path/my-app
uv sync --locked
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Generator memakai Python standard-library, menolak destination existing, memvalidasi slug/mode, menyelaraskan nama manifest/lock, menghasilkan secret baru dengan file mode 0600, dan tidak menyalin venv/data/output. Mode pilihan: fullstack, api, hybrid; domain model/migrations tetap sama.

## Yang disediakan

| Area | Implementasi |
|---|---|
| Startup | uv manifest/lock, `.python-version`, private env generator, committed migrations |
| Settings | local/test/production, fail-fast production secrets/hosts/PostgreSQL, mode routing |
| Identity | Custom AbstractUser, credential sessions, CSRF, logout POST, password flows |
| Domain | Single-owner Project scope, active actors, name/status constraints, atomic transitions |
| HTML | Search/filter/pagination, create/detail/edit, activate/archive, bound errors/empty/pending |
| REST | DRF list/create/retrieve/update, workflow actions, private OpenAPI/sidecar docs |
| Admin | Always Unfold, compatible auth forms, superuser-only identity management, scoped create/edit/filter/bulk/dialog/custom page/dashboard |
| Static | Scoped public CSS/JS, Unfold assets, compressed manifest and WhiteNoise |
| Deployment | Non-root Gunicorn Docker, PostgreSQL Compose, explicit migration step, private runtime role |
| Maintenance | Architecture/design/readme, lint, CI mode matrix, SQLite/PostgreSQL and row-lock tests |

Superuser global scope adalah policy contoh yang explicit. Tenant, JWT/SSO, provider/queue, import/export/history dan media uploads ditambahkan dari panduan terkait ketika diperlukan. Jangan mengiklankan capabilities tersebut sebagai implementasi boilerplate aktif.

## Mengembangkan domain berikutnya

1. Buat app dengan domain responsibility dan AppConfig namespace tepat.
2. Modelkan relasi, state, constraint, dan authorized scope.
3. Buat shared write operation bila rule harus konsisten pada HTML/API/admin/task.
4. Tambahkan adapters dan named URL sesuai selected surfaces.
5. Register admin Unfold dan permission-scoped navigation/data/actions.
6. Tambahkan migrations serta meaningful positive/negative tests.
7. Verifikasi path authenticated dan production/static yang terpengaruh.

Query policy bukan pengganti permission write: caller/admin role checks dan shared actor/object/state rule harus konsisten. Callback dashboard/search tidak query database saat settings diimport. Tidak ada akun demo yang otomatis ditanam atau pekerjaan eksternal yang diam-diam dijalankan.

## Verifikasi dan pemeliharaan template

Setiap perubahan template perlu diuji dari proyek hasil generator, bukan hanya source. Cek `uv sync --locked` setelah rename; smoke test ketiga modes; migration drift; tests/lint/schema; real credential/CSRF; Unfold/static; PostgreSQL locking bila transaksi berubah. Perubahan auth/role memerlukan negative tests pada admin/direct API/form URL.

Jangan menyertakan `.env`, SQLite, `.venv`, collected static, screenshots, atau test-generated project pada salinan skill. Update source dan installed copy setelah validasi. Boilerplate production belum membuktikan deployment eksternal/HTTPS proxy/SMTP provider; verifikasi environment pengguna sesuai acceptance.
