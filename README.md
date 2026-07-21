# Simple LMS – Extended Backend

Backend untuk Learning Management System (LMS) sederhana, dikembangkan sebagai Final Project mata kuliah **Pemrograman Sisi Server** — Teknik Informatika, Universitas Dian Nuswantoro.

Project ini melanjutkan Simple LMS dari tugas capstone sebelumnya, dengan tambahan **Paket 1 – LMS Experience**: search & filter course lanjutan, rating/review/wishlist, curriculum & progress belajar detail, serta student dashboard.

---

## Daftar Isi

- [Tech Stack](#tech-stack)
- [Fitur](#fitur)
- [Struktur Project](#struktur-project)
- [Cara Menjalankan (Docker Compose)](#cara-menjalankan-docker-compose)
- [Environment Variables](#environment-variables)
- [Akun Demo](#akun-demo)
- [Endpoint Utama](#endpoint-utama)
- [Dokumentasi API](#dokumentasi-api)
- [Testing](#testing)
- [Seed Data](#seed-data)
- [Kendala dan Solusi](#kendala-dan-solusi)

---

## Tech Stack

- **Python 3.12** + **Django**
- **Django Ninja** — REST API & OpenAPI/Swagger docs
- **PostgreSQL** — database utama
- **JWT Authentication** (`django-ninja-jwt` / implementasi custom)
- **Docker & Docker Compose**

---

## Fitur

### Fitur Dasar (Fondasi)

- Autentikasi JWT (register, login, refresh token)
- Role-based access control: `admin`, `instructor`, `student`
- CRUD Category & Course
- Enrollment (student mendaftar course)
- Progress belajar per lesson
- Dokumentasi API via Swagger/OpenAPI

### Fitur Tambahan — Paket 1: LMS Experience (51 poin)

| No  | Fitur                                       | Poin | Status  |
| --- | ------------------------------------------- | ---- | ------- |
| 1   | Search, filter, dan sorting course lanjutan | 12   | Selesai |
| 2   | Rating, review, dan wishlist course         | 12   | Selesai |
| 3   | Curriculum dan progress belajar detail      | 15   | Selesai |
| 4   | Student dashboard                           | 12   | Selesai |

Detail implementasi tiap fitur ada di [`FINAL_PROJECT_REPORT.md`](./FINAL_PROJECT_REPORT.md).

---

## Struktur Project

```
.
├── core/                 # Django project configuration
│   ├── settings.py       # Django settings
│   ├── urls.py           # URL routing
│   ├── asgi.py          # ASGI configuration
│   ├── wsgi.py          # WSGI configuration
│   └── __init__.py
├── courses/             # Main app - User, Category, Course, Section, Lesson, Enrollment, Review, Wishlist
│   ├── migrations/      # Database migrations
│   ├── management/      # Custom commands (seed_demo_data, etc.)
│   ├── models.py        # User, Category, Course, Section, Lesson, Enrollment, Review, Wishlist models
│   ├── schemas.py       # Pydantic schemas untuk request/response
│   ├── api.py          # Endpoint definitions (Django Ninja routes)
│   ├── views.py        # View logic
│   ├── admin.py        # Django Admin configuration
│   ├── apps.py         # App configuration
│   ├── tests.py        # Unit tests
│   └── __init__.py
├── docs/                # Postman collection, screenshots
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile          # Docker image definition
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── manage.py          # Django management script
├── jwt-signing.pem    # JWT private key (excluded from repo)
├── jwt-signing.pub    # JWT public key (excluded from repo)
├── FINAL_PROJECT_REPORT.md  # Project documentation
└── README.md
```

---

## Cara Menjalankan (Docker Compose)

### 1. Clone repository

```bash
git clone <url-repo-anda>
cd simple-lms-extended-backend
```

### 2. Siapkan file environment

```bash
cp .env.example .env
```

Sesuaikan isi `.env` bila perlu (lihat [Environment Variables](#environment-variables)).

### 3. Build dan jalankan container

```bash
docker compose up -d --build
```

Service yang akan berjalan:

| Service | Deskripsi              | Port   |
| ------- | ---------------------- | ------ |
| `web`   | Django app (Ninja API) | `8000` |
| `db`    | PostgreSQL             | `5432` |

### 4. Jalankan migration

```bash
docker compose exec web python manage.py migrate
```

### 5. Buat superuser (opsional, untuk akses Django Admin)

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Load seed/demo data

```bash
docker compose exec web python manage.py seed_demo_data
```

### 7. Akses aplikasi

- API base URL: `http://localhost:8000/api/`
- Swagger/OpenAPI docs: `http://localhost:8000/api/docs`
- Django Admin: `http://localhost:8000/admin`

### Perintah berguna lainnya

```bash
# Melihat log
docker compose logs -f web

# Masuk ke shell Django
docker compose exec web python manage.py shell

# Menjalankan test
docker compose exec web python manage.py test

# Menghentikan semua service
docker compose down

# Menghentikan dan menghapus volume database (reset total)
docker compose down -v
```

---

## Environment Variables

Contoh isi `.env.example`:

```env
# Django
DEBUG=True
SECRET_KEY=change-this-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=simple_lms
POSTGRES_USER=lms_user
POSTGRES_PASSWORD=lms_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

---

## Akun Demo

Setelah menjalankan `python manage.py seed_demo_data`, akun berikut tersedia:

| Role       | Email                 | Password           |
| ---------- | --------------------- | ------------------ |
| Admin      | `admin@lms.test`      | `Admin12345!`      |
| Instructor | `instructor@lms.test` | `Instruktur12345!` |
| Student    | `student@lms.test`    | `Students12345!`   |

Login untuk mendapatkan JWT token:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "student@lms.test", "password": "Student12345!"}'
```

Gunakan `access_token` yang dikembalikan pada header setiap request yang butuh autentikasi:

```
Authorization: Bearer <access_token>
```

---

## Endpoint Utama

### Autentikasi

| Method | Endpoint             | Deskripsi              | Role   |
| ------ | -------------------- | ---------------------- | ------ |
| POST   | `/api/auth/register` | Registrasi user baru   | Publik |
| POST   | `/api/auth/login`    | Login, mendapatkan JWT | Publik |
| POST   | `/api/auth/refresh`  | Refresh access token   | Publik |

### Course & Category

| Method | Endpoint                                              | Deskripsi                             | Role                       |
| ------ | ----------------------------------------------------- | ------------------------------------- | -------------------------- |
| GET    | `/api/courses?search=&category=&level=&status=&sort=` | List course dengan search/filter/sort | Publik                     |
| GET    | `/api/courses/{id}`                                   | Detail course                         | Publik                     |
| POST   | `/api/courses`                                        | Buat course baru                      | Instructor                 |
| PUT    | `/api/courses/{id}`                                   | Update course                         | Instructor (pemilik)/Admin |
| DELETE | `/api/courses/{id}`                                   | Hapus course                          | Instructor (pemilik)/Admin |
| GET    | `/api/categories`                                     | List kategori                         | Publik                     |

### Curriculum & Progress

| Method | Endpoint                       | Deskripsi                           | Role                 |
| ------ | ------------------------------ | ----------------------------------- | -------------------- |
| GET    | `/api/courses/{id}/curriculum` | Lihat section, lesson, dan progress | Student (enrolled)   |
| POST   | `/api/courses/{id}/sections`   | Tambah section                      | Instructor (pemilik) |
| POST   | `/api/sections/{id}/lessons`   | Tambah lesson ke section            | Instructor (pemilik) |
| POST   | `/api/lessons/{id}/complete`   | Tandai lesson selesai               | Student              |

### Enrollment

| Method | Endpoint                   | Deskripsi                | Role    |
| ------ | -------------------------- | ------------------------ | ------- |
| POST   | `/api/courses/{id}/enroll` | Enroll ke course         | Student |
| GET    | `/api/me/enrollments`      | List course yang diikuti | Student |

### Review & Wishlist

| Method | Endpoint                     | Deskripsi                     | Role               |
| ------ | ---------------------------- | ----------------------------- | ------------------ |
| POST   | `/api/courses/{id}/reviews`  | Submit/update review & rating | Student (enrolled) |
| GET    | `/api/courses/{id}/reviews`  | List review sebuah course     | Publik             |
| POST   | `/api/courses/{id}/wishlist` | Toggle wishlist course        | Student            |
| GET    | `/api/me/wishlist`           | List wishlist milik student   | Student            |

### Dashboard

| Method | Endpoint                    | Deskripsi                                      | Role       |
| ------ | --------------------------- | ---------------------------------------------- | ---------- |
| GET    | `/api/dashboard/student`    | Ringkasan course aktif, selesai, rekomendasi   | Student    |
| GET    | `/api/dashboard/instructor` | Statistik course & enrollment milik instructor | Instructor |

Postman collection lengkap tersedia di [`docs/postman_collection.json`](./docs/postman_collection.json).

---

## Dokumentasi API

Swagger/OpenAPI otomatis tersedia setelah project berjalan:

```
http://localhost:8000/api/docs
```

---

## Testing

```bash
docker compose exec web python manage.py test
```

Menjalankan test untuk app tertentu saja:

```bash
docker compose exec web python manage.py test apps.reviews
```

Test yang tersedia mencakup:

- Autentikasi & permission per role
- Endpoint course, enrollment, progress dasar
- Fitur tambahan: search/filter, review/wishlist, curriculum progress, dashboard

---

## Seed Data

Command `seed_demo_data` akan membuat:

- 3 akun demo (admin, instructor, student)
- Beberapa kategori dan course contoh
- Section & lesson contoh untuk masing-masing course
- Beberapa enrollment, review, dan progress contoh

```bash
docker compose exec web python manage.py seed_demo_data
```

Untuk reset data demo:

```bash
docker compose exec web python manage.py flush --no-input
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_demo_data
```

---

## Kendala dan Solusi

| Kendala                                                         | Solusi                                                                                                     |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Migration gagal karena data `Lesson` lama belum punya `section` | Membuat data migration untuk generate "Default Section" per course sebelum field `section` dijadikan wajib |
| Query N+1 saat menampilkan rating rata-rata di list course      | Menggunakan `annotate(Avg("reviews__rating"))` alih-alih looping manual                                    |

---

## Kontributor

- **Nama:** NABHAAN AURYSHAFA ADHIGANA
- **NIM:** A11.2023.15254
- **Kelas:** A11.4618
- **Mata Kuliah:** Pemrograman Sisi Server (A11.4618)
- **Pengajar:** Fahri Firdausillah, S.Kom, M.CS
