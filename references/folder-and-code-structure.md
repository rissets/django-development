# Struktur folder dan kode

Gunakan bentuk yang cukup untuk ukuran aplikasi; pertahankan bentuk proyek existing. Contoh berikut merupakan konvensi skill untuk proyek baru, bukan persyaratan framework.

## Struktur awal untuk aplikasi kecil

```text
project/
├── manage.py
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
├── .gitignore
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── accounts/
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   └── migrations/
│   └── projects/
│       ├── apps.py
│       ├── models.py
│       ├── forms.py
│       ├── views.py
│       ├── urls.py
│       ├── admin.py
│       ├── tests.py
│       ├── migrations/
│       ├── templates/projects/
│       └── static/projects/
├── templates/
│   ├── base.html
│   ├── registration/login.html
│   └── components/
└── static/
    ├── css/app.css
    └── js/app.js
```

Untuk aplikasi kecil, models/views/forms/admin satu file cukup. `services.py`, `selectors.py`, API package, jobs, atau integrations tidak perlu dibuat kosong. App templates/static diberi namespace supaya nama seperti `detail.html`/`style.css` tidak bertabrakan. `staticfiles/`, `media/`, `.venv/`, database lokal, dan caches adalah runtime output, bukan source.

## Struktur saat domain tumbuh

```text
project/
├── config/
│   ├── settings/{base,local,test,production}.py
│   ├── urls.py
│   ├── unfold.py
│   ├── celery.py                  # jika dipakai
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── accounts/
│   ├── organizations/             # jika membership/tenant diperlukan
│   └── projects/
│       ├── apps.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── project.py
│       │   └── activity.py
│       ├── querysets.py
│       ├── policies.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── projects.py
│       ├── forms.py
│       ├── views/{__init__,projects}.py
│       ├── urls.py
│       ├── api/
│       │   ├── serializers.py
│       │   ├── views.py
│       │   └── urls.py
│       ├── admin/{__init__,projects}.py
│       ├── admin_views.py
│       ├── admin_components.py
│       ├── tasks.py                # jika dipakai
│       ├── integrations/            # external API boundary
│       ├── management/commands/
│       ├── migrations/
│       ├── tests/
│       │   ├── test_services.py
│       │   ├── test_permissions.py
│       │   ├── test_api.py
│       │   └── test_views.py
│       ├── templates/projects/
│       └── static/projects/
├── templates/{components,registration,admin}/
├── static/{css,js,images}/
├── docs/{architecture,design,operations}/
└── deploy/                          # jika deployment artifacts diperlukan
```

Pecah modul ketika tanggung jawab atau ukuran sudah menghambat navigasi/review, bukan berdasarkan batas baris universal. Jangan menyimpan file dan package dengan nama sama (`models.py` bersama `models/`). Saat split, re-export models pada `models/__init__.py` agar Django menemukannya; import registrations pada `admin/__init__.py` agar autodiscovery bekerja. `views`/services tidak harus re-export semua simbol, gunakan imports eksplisit.

## Aturan dependency

```text
HTML views ── forms ─────┐
DRF views ── serializers├── shared workflow ── models/querysets ── database
Unfold actions/forms ───┤          │
tasks/commands ─────────┘          └── integration adapter / after-commit enqueue
```

Domain/query layer tidak mengimpor `request`, DRF Response, template rendering, atau ModelAdmin. Adapter menerima request, menentukan actor/scope, memvalidasi transport, memanggil domain, dan mengubah hasil/errors menjadi response. Task mendapatkan identifier/context minimal dan memeriksa scope/state sesuai kontraknya, bukan memegang HttpRequest.

App boleh bergantung pada domain app lain bila relasi bisnis membutuhkannya; deklarasikan dependency dan hindari circular imports. Jangan membuat `core`/`utils` menjadi tempat semua kode. Letakkan helper dekat pemakai; pindahkan ke shared module hanya bila beberapa domain benar-benar memakai konsep yang sama.

## Nama dan API internal

- Function/use case: kata kerja domain jelas, misalnya `create_project`, `approve_order`, `reserve_stock`.
- Query/selector: nama hasil/scope, misalnya `visible_to`, `pending_orders`, bukan `get_data`.
- Exception: kondisi domain, misalnya `InvalidProjectTransition`; transport adapter menentukan HTTP statusnya.
- Model: singular PascalCase; fields/functions snake_case. Nama URL mencerminkan resource/action dan namespace app.
- Settings: konfigurasi murni; hindari melakukan query atau network ketika module diimport.
- DTO/dataclass dipakai untuk kontrak yang benar-benar membutuhkan bentuk terpisah; tidak wajib mengubah setiap model menjadi DTO.

Use case signature dianjurkan keyword-only untuk konteks/actor yang mudah tertukar:

```python
def create_project(*, actor, name: str):
    ...
```

Ellipsis di sini hanya ilustrasi signature; implementasi lengkap berada pada [vertical slice](vertical-slice.md). Jangan mengirim stub ini sebagai feature selesai.

## Pembagian validation

| Rule | Tempat utama | Proteksi tambahan |
|---|---|---|
| Format/required HTML | Form | Domain untuk caller lain |
| Format/required JSON | Serializer | Domain untuk caller lain |
| Invariant satu object | Model method/validator atau domain | DB constraint jika bisa |
| Invariant antar-row/state | Shared workflow | Atomic/locking/constraint |
| Hak actor/tenant | Policy/scope + workflow | Adapter/action/object check |
| Uniqueness concurrent | DB constraint | Form/serializer untuk feedback |
| Presentasi conditional | Template/Unfold | Server validation tidak hilang |

## Import, typing, dan dokumentasi kode

Gunakan import grup standard-library, dependency, project mengikuti formatter. Jangan memakai wildcard kecuali konvensi settings yang memang terdefinisi dan terkontrol; settings overrides sebaiknya sedikit dan jelas. String model references mengurangi cycles pada FK; gunakan `get_user_model()` pada runtime.

Type annotate workflow/integration boundaries bila bermanfaat. Django models/querysets memerlukan type tooling yang kompatibel; jangan menambahkan `Any` luas hanya agar checker diam. Docstring menjelaskan invariant, side effects, concurrency, dan exception penting. Komentar menjelaskan alasan; hapus komentar yang hanya mengulang nama metode.

Serializers/forms/admin bukan tempat menghitung policy/arithmetic yang berbeda-beda untuk operasi yang sama. Jangan mengimpor serializer ke domain untuk menggunakan validasinya. Extract rule yang shared sebagai callable independen dari transport.

## Perubahan struktur existing

Trace imports, URL mappings, migrations, tasks autodiscovery, admin registration, template paths, dan tests sebelum move. Preserve module paths yang dipakai migration historical references; jangan mengganti import path callable migration tanpa kompatibilitas. Sesuaikan AppConfig, packaging, settings entrypoints, and deployment commands. Satu refactor sebaiknya tidak sekaligus upgrade dependency dan mengubah behavior tanpa kebutuhan.

## Review sebelum selesai

Ada caller nyata untuk modul baru; domain boundaries dapat dijelaskan; registrasi/import benar; form/API writable fields explicit; permission konsisten; tidak ada per-row query tersembunyi; template/static namespaced; migration ikut source; secrets/output di-ignore; commands deployment menunjuk settings yang benar. Lihat [arsitektur](architecture-and-code.md) untuk transaksi dan database.
