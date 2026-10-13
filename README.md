# Django Development

Skill Codex untuk pengembangan aplikasi Django fullstack dan REST API, dengan **Django Unfold sebagai standar admin**.

Versi: **0.1.0**. Panduan utama: [SKILL.md](SKILL.md). Riwayat rilis: [CHANGELOG.md](CHANGELOG.md).

## Instalasi skill

Clone repository ini langsung sebagai satu folder skill. Direktori tujuan harus belum ada:

```bash
git clone https://github.com/rissets/django-development.git \
  ~/.codex/skills/django-development
```

Untuk versi rilis yang tetap, jalankan `git checkout v0.1.0` di direktori tersebut. Jika skill sudah terpasang, simpan perubahan lokal sebelum memperbarui salinannya. Repository ini privat; akses GitHub yang sesuai diperlukan.

## Pemakaian di Codex

Sebutkan skill dan kebutuhan aplikasi dalam chat:

```text
Gunakan $django-development untuk membuat aplikasi inventaris.
Mode hybrid, PostgreSQL, admin Unfold.
Implementasikan produk, kategori, transaksi stok dan permission.
```

Untuk existing project, buka folder proyek lalu minta skill mempelajari arsitektur sebelum melakukan perubahan. Skill memandu Codex menggunakan tools file/terminal yang tersedia; skill ini tidak memiliki server MCP terpisah.

## Memulai dari boilerplate

Prasyarat: Python 3.12–3.14 dan uv. Generator hanya membutuhkan Python standard library; instalasi dependencies menggunakan uv.

```bash
python3 ~/.codex/skills/django-development/scripts/create_project.py \
  ~/Dev/aplikasi-baru --name aplikasi-baru --mode hybrid

cd ~/Dev/aplikasi-baru
uv sync --locked
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Generator menolak folder tujuan yang sudah ada dan membuat `.env` dengan secret unik, izin 0600, tanpa mencetak nilainya. Pilihan mode: `fullstack`, `api`, `hybrid`; admin selalu Unfold.

Panduan aplikasi, routes, testing, deployment dan maintenance tersedia di [README boilerplate](assets/boilerplate/README.md). Jika menggunakan ZIP boilerplate tanpa generator, buat `.env` lokal dengan `python3 scripts/init_env.py --mode hybrid` sebelum menjalankan Django.

## Isi repository

| Folder/file | Fungsi |
|---|---|
| `SKILL.md` | Instruksi agent dan routing panduan |
| `references/` | 18 panduan pengembangan, Unfold, design dan maintenance |
| `scripts/create_project.py` | Generator proyek |
| `scripts/test_create_project.py` | Tests generator |
| `assets/boilerplate/` | Aplikasi runnable dengan migrations, lockfile, templates, API, Unfold, tests dan Docker |
| `agents/openai.yaml` | Metadata antarmuka skill |

Baseline aplikasi memakai single-owner Project dan lifecycle draft/active/archived. Sesuaikan model bisnis, tenant, autentikasi tambahan dan integrasi sesuai kebutuhan. Documentation package merupakan snapshot riset; cek installed versions dan official docs saat implementasi/upgrade. Bahan buku/PDF tidak dibundel dalam repository skill ini.

## Verifikasi lokal

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Lanjutkan tests aplikasi dari proyek hasil generator sesuai README boilerplate. Rilis awal telah divalidasi pada tiga mode, schema API, browser desktop/mobile dan Docker; PostgreSQL 17 menjalankan 26 tests tanpa skip. External hosting/TLS, SMTP provider dan CI remote belum diverifikasi.
