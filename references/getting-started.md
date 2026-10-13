# Memulai proyek Django

Panduan ini untuk proyek baru. Untuk proyek existing, lakukan discovery dan adaptasi tanpa menjalankan `startproject` di atas aplikasi yang sudah ada. Versi contoh dipilih setelah memeriksa dukungan Python/Django/paket; angka bukan janji versi terbaru.

**Jalur runnable:** gunakan [bundled boilerplate](boilerplate.md) bila starter sesuai. Generator menyediakan settings, auth templates, domain, HTML/API/admin, migrations, lock dan tests lengkap. Langkah manual berikut menjelaskan fondasi dan keputusan, bukan pengganti seluruh aplikasi hasil generator.

## 1. Tentukan produk dan acceptance

Catat aktor, workflow pertama, objek utama, relasi, state, izin, dan hasil terlihat. Pilih mode:

| Mode | Rendering | Kontrak input | Admin |
|---|---|---|---|
| Fullstack | Django templates | Form/ModelForm | Unfold |
| API | DRF JSON + frontend/client terpilih | Serializer | Unfold jika admin tersedia |
| Hybrid | Keduanya, berbagi domain | Adapter HTML/API terpisah | Unfold |

Mulai dari satu workflow nyata, misalnya pengguna membuat proyek miliknya lalu melihatnya pada daftar/detail. Untuk tenant, rancang membership/scope sebelum membuat endpoint atau dashboard. Tentukan apakah staf memiliki global grant atau grant per tenant; jangan menyamakan `is_staff` dengan akses semua data.

## 2. Buat environment dan dependency

Gunakan package manager proyek. Untuk proyek baru yang belum memiliki konvensi, uv adalah pilihan praktis. Contoh berikut mempertahankan Django 6.1 series; ganti rentangnya jika compatibility review memilih supported series lain.

```bash
mkdir django-app
cd django-app
uv init --bare --python 3.12
uv add 'Django>=6.1,<6.2' django-unfold django-environ whitenoise
uv add --dev ruff
uv run django-admin startproject config .
mkdir -p apps/accounts apps/projects
touch apps/__init__.py
uv run python manage.py startapp accounts apps/accounts
uv run python manage.py startapp projects apps/projects
```

Untuk API/hybrid saja:

```bash
uv add djangorestframework drf-spectacular
```

PostgreSQL bila dibutuhkan:

```bash
uv add 'psycopg[binary]'
```

Jangan menambah Celery, Redis, Channels, allauth, atau frontend build hanya karena tersedia. Pilih setelah workflow membutuhkan kemampuan tersebut. Commit manifest/lock, bukan `.venv`, `.env`, SQLite lokal, uploads, atau generated static. [uv projects](https://docs.astral.sh/uv/guides/projects/)

## 3. App namespace dan user model sebelum migrasi

`apps/accounts/apps.py`:

```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
```

`apps/projects/apps.py` memakai pola yang sama dengan `name = "apps.projects"`. App label tetap `accounts`/`projects`; nama package Python mencakup `apps.`. Jangan mengubah label existing tanpa migration analysis.

`apps/accounts/models.py`:

```python
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass
```

Untuk kebutuhan identitas yang cocok, ini memberikan titik ekstensi awal tanpa mengganti auth backend. Tambahkan hanya field yang dipakai. Set `AUTH_USER_MODEL = "accounts.User"` sebelum `makemigrations`/`migrate` pertama. Proyek existing dengan user default tidak boleh dipindahkan ke custom user secara otomatis. [Custom authentication](https://docs.djangoproject.com/en/6.1/topics/auth/customizing/)

## 4. Settings yang jelas

Pada proyek kecil, satu `config/settings.py` dengan typed environment cukup. Bila local/test/production membutuhkan override terpisah, ubah menjadi `config/settings/{__init__,base,local,test,production}.py` dan sesuaikan `DJANGO_SETTINGS_MODULE` di manage.py, WSGI/ASGI, CI, worker. Jangan meninggalkan dua `settings.py` dan package settings yang ambigu.

Berikut konfigurasi **tambahan/pengganti terpilih**, bukan settings Django lengkap. Pertahankan `TEMPLATES`, validator password, middleware sessions/auth/messages, dan konfigurasi lain yang dihasilkan `startproject`.

```python
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent  # config/settings.py
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
DATABASES = {"default": env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
AUTH_USER_MODEL = "accounts.User"
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

Untuk `config/settings/base.py`, BASE_DIR naik satu tingkat lagi: `.parent.parent.parent`. Local boleh memakai SQLite; production module mewajibkan `DATABASE_URL`/host/secret yang benar, bukan diam-diam fallback ke local. Tetapkan bahasa/timezone sesuai produk, dengan `USE_TZ = True`.

Urutan dasar `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts.apps.AccountsConfig",
    "apps.projects.apps.ProjectsConfig",
]
```

Sisipkan integration apps Unfold **yang dipakai** setelah Unfold dan sebelum paket yang templatenya dioverride. Untuk API tambahkan `rest_framework`, `drf_spectacular`; `django_filters` hanya jika dipakai. Letakkan WhiteNoise tepat setelah SecurityMiddleware, lalu pertahankan sisa urutan bawaan. [Unfold setup](https://unfoldadmin.com/docs/installation/quickstart/), [WhiteNoise](https://whitenoise.readthedocs.io/en/stable/django.html)

Tambahkan `BASE_DIR / "templates"` pada `TEMPLATES[0]["DIRS"]` bila ada shared templates, dan `STATICFILES_DIRS` hanya jika direktori source static tersebut benar-benar ada. Jangan set STATIC_ROOT sama dengan source static.

## 5. Rahasia dan environment lokal

Commit `.env.example` berisi nama dan nilai non-rahasia, dengan secret kosong. `.env` harus di-ignore. Contoh:

```dotenv
DJANGO_SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Isi secret lokal dengan generator Django atau secret manager tanpa memasukkan nilainya ke chat/log. Untuk local-only onboarding, program berikut memakai token acak standard-library yang aman untuk parsing `.env`, menulisnya tanpa mencetak nilai, dan menolak overwrite:

```python
from pathlib import Path
from secrets import token_urlsafe

target = Path(".env")
with target.open("x") as stream:
    stream.write(f"DJANGO_SECRET_KEY={token_urlsafe(50)}\n")
    stream.write("DEBUG=True\nALLOWED_HOSTS=localhost,127.0.0.1\n")
target.chmod(0o600)
```

Untuk production, inject environment/secret melalui deployment system; jangan menjalankan generator untuk mengganti secret proyek existing.

## 6. URL, login, dan admin

Pertahankan `path("admin/", admin.site.urls)`. Register custom User/Group memakai Unfold auth forms dan class recipe pada [Unfold](unfold-admin.md). Untuk fullstack pilih Django login/logout/password flows atau allauth sesuai kebutuhan; sediakan template login, `LOGIN_URL`, redirect yang valid, dan permission decorators/mixins. Jangan menganggap login admin otomatis menjadi customer account UX.

Untuk API tambahkan router, schema/docs paths, auth dan permission defaults dari [REST API](rest-api.md). Public endpoint harus merupakan keputusan eksplisit. Nav/sidebar menggunakan nama URL yang memang telah diregistrasikan.

## 7. Bangun vertical slice

Ikuti [struktur](folder-and-code-structure.md) dan [contoh terhubung](vertical-slice.md): model/constraint, migration, queryset scope, Form/serializer, workflow, HTML/API adapter, Unfold admin, lalu result state. Implementasikan invalid input dan denied access bersamaan dengan jalur sukses.

Jangan menjalankan migrasi custom user sebelum model/settings siap. Setelah itu, pada database development yang diotorisasi:

```bash
uv run python manage.py makemigrations accounts projects
uv run python manage.py migrate
uv run python manage.py check
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

`createsuperuser` interaktif; kredensial tidak disimpan ke source. `runserver` hanya development. Saat verifikasi customer flow, gunakan actor biasa selain superuser. Jangan memakai SQLite untuk membuktikan locking PostgreSQL.

## 8. Selesai bila slice bekerja

Checklist: URL dapat dibuka; aktor bisa login; form/API menerima invalid dan valid input; database state benar; owner lain ditolak; admin styled dan role-scoped; CSS/JS tersedia; tests/checks yang relevan lulus; tidak ada tombol tanpa tujuan. Lanjutkan modul berikut setelah fondasi ini terbukti.

Sebelum deployment: production settings, build/collectstatic, real DB/backup, HTTPS/proxy/cookies, schema visibility, worker bila ada, dan authenticated smoke path. Detail pada [produksi](production-and-verification.md). Sebuah scaffold bukan aplikasi selesai.
