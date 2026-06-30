# Dokumentasi Fitur Website Rekomendasi Buku BookAI

## 1. Gambaran Umum

BookAI adalah website rekomendasi dan ringkasan buku berbasis Django. Website ini membantu pengguna mencari buku dari OpenLibrary API, melihat buku populer berdasarkan jumlah favorit, menyimpan buku ke daftar favorit, membuat ringkasan buku menggunakan AI, serta mengirim feedback kepada admin.

Secara umum, sistem terdiri dari:

- Frontend: HTML template Django, CSS custom, JavaScript vanilla.
- Backend: Python Django.
- Database: MySQL sesuai konfigurasi aktif pada `settings.py`.
- API eksternal: OpenLibrary API untuk data buku dan cover.
- AI: Groq API dengan model `llama-3.3-70b-versatile` untuk membuat ringkasan buku.
- Autentikasi: Django Authentication dan django-allauth untuk opsi Google login.

## 2. Struktur File Utama

```text
website_rekomendasi_buku fix/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── db_buku
├── website_rekomendasi_buku/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── main/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/
│       ├── base.html
│       ├── home.html
│       ├── ringkasan_ai.html
│       ├── favorites.html
│       ├── popular-books.html
│       ├── contact.html
│       ├── messages.html
│       ├── about.html
│       ├── auth/
│       │   ├── login.html
│       │   ├── register.html
│       │   └── verify_otp.html
│       └── components/
│           ├── navbar.html
│           ├── book_modal.html
│           └── login_required_modal.html
└── venv/
```

Keterangan:

- `website_rekomendasi_buku/settings.py`: konfigurasi project, database, static files, email, allauth, dan API key AI.
- `website_rekomendasi_buku/urls.py`: URL root, admin, allauth, dan routing ke aplikasi `main`.
- `main/models.py`: struktur tabel aplikasi.
- `main/views.py`: logika fitur backend.
- `main/urls.py`: daftar endpoint halaman dan API.
- `main/templates/`: tampilan HTML.
- `main/static/css/style.css`: seluruh desain visual.
- `main/static/js/app.js`: interaksi frontend, modal, fetch API, favorit, dan OTP input.
- `main/tests.py`: test dasar autentikasi dan feedback.

## 3. Teknologi yang Digunakan

Backend:

- Python.
- Django 4.2.23.
- django-allauth 65.18.0 untuk integrasi akun sosial Google.
- mysqlclient dan PyMySQL untuk koneksi MySQL.
- requests untuk mengambil data OpenLibrary.
- groq untuk integrasi AI.

Frontend:

- HTML5.
- CSS3 custom.
- JavaScript vanilla.
- Django Template Language.
- Google Fonts.
- SVG inline untuk ikon.

Database:

- Konfigurasi aktif memakai MySQL:
  - engine: `django.db.backends.mysql`
  - nama database: `db_buku`
  - host: `localhost`
  - port: `3306`
- File `db.sqlite3` dan `db_buku` masih ada di folder project, tetapi konfigurasi Django saat ini mengarah ke MySQL.

API dan layanan eksternal:

- OpenLibrary Search API: mencari buku berdasarkan judul.
- OpenLibrary Covers API: mengambil cover buku berdasarkan `cover_id`.
- Groq API: membuat ringkasan AI.
- SMTP Gmail: konfigurasi email sudah ada, tetapi sebaiknya credential ditaruh di `.env`, bukan ditulis langsung di kode.

## 4. Desain Frontend

Identitas visual:

- Nama aplikasi: BookAI.
- Warna utama: ungu `#6C3FC5`.
- Ungu muda: `#8B5CF6`.
- Ungu gelap: `#4C1D95`.
- Background utama: lavender muda `#EEEAF8`.
- Card: putih `#FFFFFF`.
- Teks utama: `#1A1025`.
- Teks sekunder: `#6B6580`.
- Border: `#D8D0F0`.
- Warna error: `#EF4444`.
- Warna sukses: `#22C55E`.

Font:

- Judul: `Playfair Display`, serif.
- Isi/body: `DM Sans`, sans-serif.

Komponen frontend utama:

- Navbar sticky berwarna ungu.
- Tombol login, daftar, logout, dan avatar.
- Hero section pada halaman Home.
- Search bar berbentuk pil.
- Grid buku horizontal.
- Card buku dengan cover, judul, author, hover overlay, dan badge ranking.
- Modal detail buku.
- Modal login required untuk pengguna yang belum login.
- Form autentikasi.
- Form feedback.
- Card pesan dan balasan admin.
- Tampilan favorit dua kolom.
- Halaman AI dengan hero gradient dan hasil ringkasan.

Responsivitas:

- Pada layar kecil, hero berubah menjadi layout satu kolom.
- Gambar hero disembunyikan di mobile.
- Modal berubah menjadi vertikal.
- Grid favorit berubah menjadi satu kolom.
- Grid buku tetap horizontal scroll agar cover tidak terlalu kecil.

## 5. Halaman dan Fitur Pengguna

### 5.1 Navbar

File: `main/templates/components/navbar.html`

Menu yang tersedia:

- Home.
- Ringkasan AI.
- Favorites.
- About Us.
- Feedback, khusus user biasa.
- Pesan Saya untuk user biasa.
- Pesan untuk admin/staff.
- Login dan Daftar untuk pengguna belum masuk.
- Username dan Logout untuk pengguna yang sudah login.

Navbar juga memberi class `active` pada halaman yang sedang dibuka.

### 5.2 Home

File: `main/templates/home.html`

Fitur:

- Hero dengan judul "Discover your next favorite book with AI".
- Gambar dekoratif buku dari Unsplash.
- Search bar untuk mencari buku.
- Pencarian otomatis ketika user mengetik, dengan delay 500 ms.
- Pencarian juga bisa dilakukan dengan tombol Enter.
- Hasil pencarian muncul pada section "buku yang anda cari".
- Jika tidak ada hasil, muncul empty state.
- Section "buku populer" menampilkan data dari endpoint `/api/popular/?detail=1`.
- Link "View all" menuju halaman buku populer.

Catatan teknis:

- Placeholder search menyebut "books, authors, or topics", tetapi backend saat ini mencari berdasarkan judul melalui parameter `title` OpenLibrary.

### 5.3 Login

File: `main/templates/auth/login.html`

Fitur:

- Form login dengan input username/email dan password.
- Tombol "Masuk dengan Google" ke `/accounts/google/login/`.
- Link ke halaman register.
- Menampilkan pesan error jika login gagal.
- Link "Lupa password?" tampil, tetapi belum diarahkan ke fitur reset password aktif.

Backend:

- View: `login_view`.
- Menggunakan `authenticate()` dan `login()` Django.
- Jika berhasil, user diarahkan ke Home.
- Sistem menyimpan riwayat login ke tabel `LoginHistory`, termasuk user, email, IP address, dan waktu login.
- Jika akun belum aktif, sistem memberi pesan agar user verifikasi email.

### 5.4 Register

File: `main/templates/auth/register.html`

Fitur:

- Form pendaftaran berisi username, email, password, dan konfirmasi password.
- Tombol "Daftar dengan Google" ke `/accounts/google/login/`.
- Validasi field kosong.
- Validasi password dan konfirmasi password harus sama.
- Validasi email unik.
- Validasi username unik.
- Jika berhasil, akun dibuat dan user diarahkan ke halaman login.

Backend:

- View: `register_view`.
- Menggunakan `User.objects.create_user()`.
- Pada kode aktif, user langsung dibuat aktif (`is_active=True`) dan tidak dipaksa OTP.

### 5.5 Verify OTP

File: `main/templates/auth/verify_otp.html`

Fitur yang tersedia di kode:

- Halaman input OTP 6 digit.
- Auto focus ke input berikutnya ketika user mengetik.
- Backspace kembali ke input sebelumnya.
- Validasi OTP dengan model `EmailOTP`.

Catatan status:

- Model dan halaman OTP tersedia.
- View `verify_otp` tersedia.
- Namun alur register aktif saat ini langsung mengaktifkan akun dan redirect ke login, sehingga OTP belum menjadi bagian utama dari alur register.

### 5.6 Logout

Backend:

- View: `logout_view`.
- Menggunakan `logout()` Django.
- Setelah logout, user diarahkan ke halaman login.

### 5.7 Pencarian Buku

Endpoint: `/api/search/?q=judul&page=1`

Fitur:

- Mengambil query dari parameter `q`.
- Jika kosong, mengembalikan data kosong.
- Jika user login, query disimpan ke `SearchHistory`.
- Mengambil data dari OpenLibrary Search API.
- Limit hasil per request: 20 buku.
- Data yang dikembalikan:
  - key buku.
  - title.
  - author.
  - year.
  - cover_url.
  - language.
  - description.
  - status is_favorite.

Catatan:

- Bahasa diformat dari kode seperti `eng`, `ind`, `fre` menjadi nama bahasa seperti English atau Indonesian.

### 5.8 Detail Buku

Endpoint: `/api/book-detail/?title=...&key=...`

Fitur:

- Mengambil metadata tambahan dari OpenLibrary.
- Memilih hasil terbaik berdasarkan kecocokan key, judul, tahun, bahasa, cover, dan author.
- Mengembalikan tahun, bahasa, cover, author, dan deskripsi.
- Dipakai oleh modal ketika data awal belum lengkap.

### 5.9 Modal Detail Buku

File:

- `main/templates/components/book_modal.html`
- `main/static/js/app.js`

Fitur:

- Dibuka ketika user klik card buku.
- Menampilkan cover atau fallback icon buku.
- Menampilkan title, author, tahun, bahasa, dan deskripsi.
- Jika metadata belum lengkap, JavaScript memanggil endpoint detail buku.
- Tombol "Tambah ke Favorit" atau "Hapus dari Favorit".
- Modal bisa ditutup dengan tombol X, klik overlay, atau tombol Escape.

### 5.10 Favorit atau Wishlist

Halaman: `/favorites/`

Endpoint toggle: `/api/favorite/toggle/`

Fitur:

- User login dapat menambahkan buku ke favorit.
- Jika user belum login dan menekan favorit, muncul modal login required.
- Jika buku sudah ada di wishlist, toggle akan menghapusnya.
- Jika belum ada, toggle akan menyimpannya.
- Halaman favorit menampilkan:
  - jumlah buku tersimpan.
  - cover.
  - judul.
  - author.
  - badge "Buku" atau "Ringkasan AI".
  - deskripsi atau ringkasan singkat.
  - tanggal disimpan.
  - modal detail ketika card diklik.

Data favorit disimpan pada model `Wishlist`.

### 5.11 Buku Populer

Halaman: `/popular-books/`

Endpoint: `/api/popular/?limit=50`

Fitur:

- Menampilkan buku berdasarkan jumlah wishlist terbanyak.
- Pada Home ditampilkan versi compact dengan ranking.
- Pada halaman Buku Populer ditampilkan sampai 50 buku.
- Bisa mengambil detail tambahan jika parameter `detail=1`.
- Jika belum ada data wishlist, halaman menampilkan empty state.

Logika backend:

- Query `Wishlist.objects.values(...).annotate(wishlist_count=Count('id')).order_by('-wishlist_count')`.

### 5.12 Ringkasan AI

Halaman: `/ringkasan-ai/`

Fitur:

- User wajib login.
- Form input judul buku.
- Sistem mengambil metadata buku dari OpenLibrary.
- Sistem mengirim prompt ke Groq AI.
- Output AI diharapkan berbentuk JSON.
- Hasil ditampilkan berupa:
  - cover buku.
  - judul.
  - ringkasan.
  - poin penting.
  - cocok untuk siapa.
- Hasil ringkasan otomatis disimpan ke `Wishlist` dengan `book_key` format `ai-{judul}`.
- Dari hasil AI, user bisa membuka modal detail atau menuju halaman favorit.

Catatan penting:

- Backend aktif menggunakan Groq dengan model `llama-3.3-70b-versatile`.
- Di komentar dan tampilan masih ada teks "Gemini AI", tetapi kode aktual memanggil Groq.
- `GEMINI_API_KEY` dan konfigurasi DeepSeek ada di settings, namun tidak digunakan oleh view aktif untuk ringkasan.

Prompt AI yang digunakan di kode:

```text
Buat ringkasan buku "{book_title}" dalam Bahasa Indonesia.

Berikan output JSON VALID tanpa markdown.

Format:

{
    "ringkasan": "ringkasan minimal 150 kata",
    "poin_penting": [
        "poin 1",
        "poin 2",
        "poin 3",
        "poin 4"
    ],
    "cocok_untuk": [
        "Mahasiswa",
        "Karyawan",
        "Pengusaha"
    ]
}
```

### 5.13 Feedback

Halaman: `/contact/`

Fitur:

- Hanya untuk user biasa, bukan admin.
- Admin yang membuka `/contact/` akan diarahkan ke halaman pesan.
- Form berisi nama dan pesan.
- Email diambil otomatis dari akun login.
- Pesan wajib diisi.
- Maksimal pesan 200 karakter.
- Frontend menghitung karakter secara real time.
- Jika berhasil, data masuk ke tabel `Contact`.
- Setelah terkirim, user diarahkan ke halaman Pesan.

### 5.14 Pesan Saya dan Pesan Admin

Halaman: `/messages/`

Fitur untuk user biasa:

- Melihat feedback yang pernah dikirim.
- Melihat status "Baru" atau "Dibalas".
- Melihat balasan admin jika sudah ada.

Fitur untuk admin/staff/superuser:

- Melihat seluruh feedback pengguna.
- Membalas pesan.
- Mengedit balasan yang sudah ada.
- Menghapus pesan.
- Melihat nama, email, username, tanggal pesan, dan status.

Backend:

- `message_list`: membedakan tampilan admin dan user biasa.
- `reply_message`: hanya admin yang boleh membalas.
- `delete_message`: hanya admin yang boleh menghapus.

### 5.15 About Us

Halaman: `/about/`

Isi:

- Penjelasan tentang BookAI.
- Penjelasan cara kerja BookAI.
- Penjelasan teknologi OpenLibrary API dan AI.
- Profil tim pengembang:
  - Database.
  - Frontend.
  - Backend.
  - Ide dan struktur.
  - QA dan dokumentasi.

Catatan:

- About page masih menyebut DeepSeek AI sebagai alur pencarian, tetapi implementasi aktif pada kode pencarian hanya memakai OpenLibrary, sedangkan AI aktif dipakai pada fitur ringkasan melalui Groq.

## 6. Struktur Backend

### 6.1 URL Project

File: `website_rekomendasi_buku/urls.py`

Routing utama:

- `/admin/`: Django admin.
- `/accounts/`: django-allauth, termasuk Google login.
- `/`: semua route aplikasi `main`.

### 6.2 URL Aplikasi

File: `main/urls.py`

Route:

- `/`: Home.
- `/api/popular/`: API buku populer.
- `/api/search/`: API pencarian buku.
- `/api/book-detail/`: API detail buku.
- `/ringkasan-ai/`: halaman ringkasan AI.
- `/popular-books/`: halaman buku populer.
- `/favorites/`: halaman favorit.
- `/contact/`: halaman feedback.
- `/messages/`: halaman pesan.
- `/messages/<id>/reply/`: balas pesan.
- `/messages/<id>/delete/`: hapus pesan.
- `/about/`: halaman about.
- `/api/favorite/toggle/`: toggle favorit.
- `/login/`: login.
- `/register/`: register.
- `/verify-otp/`: verifikasi OTP.
- `/logout/`: logout.

### 6.3 Helper Backend

Helper di `views.py`:

- `_format_language(language)`: mengubah kode bahasa menjadi nama bahasa.
- `_openlibrary_doc_to_meta(item)`: mengubah response OpenLibrary menjadi metadata standar.
- `_cover_id_from_url(cover_url)`: mengambil cover ID dari URL cover.
- `_score_openlibrary_doc(item, title, book_key)`: memberi skor agar metadata yang dipilih paling relevan.
- `_fetch_openlibrary_meta(title, book_key)`: mengambil metadata dari OpenLibrary.
- `_is_admin_user(user)`: mengecek apakah user staff atau superuser.

## 7. Struktur Database

### 7.1 Wishlist

Fungsi:

- Menyimpan buku favorit pengguna.
- Menyimpan hasil ringkasan AI dalam wishlist.

Field:

- `user`: relasi ke User.
- `book_key`: key unik buku dari OpenLibrary atau key buatan `ai-{judul}`.
- `title`: judul buku.
- `author`: penulis.
- `cover_id`: ID cover OpenLibrary.
- `ai_summary`: ringkasan AI.
- `ai_points`: poin penting dari AI dalam JSON.
- `ai_targets`: target pembaca dari AI dalam JSON.
- `created_at`: waktu penyimpanan.

### 7.2 SearchHistory

Fungsi:

- Menyimpan riwayat pencarian user.

Field:

- `user`.
- `query`.
- `created_at`.

### 7.3 AIRecommendation

Fungsi:

- Disiapkan untuk menyimpan input dan hasil AI.

Field:

- `user`.
- `input_text`.
- `result`.
- `created_at`.

Catatan:

- Model ini terdaftar di admin, tetapi belum dipakai oleh view aktif.

### 7.4 LoginHistory

Fungsi:

- Menyimpan riwayat login.

Field:

- `user`.
- `email`.
- `ip_address`.
- `logged_in_at`.

### 7.5 SavedSummary

Fungsi:

- Disiapkan untuk menyimpan ringkasan AI secara terpisah.

Field:

- `user`.
- `title`.
- `cover_url`.
- `summary`.
- `points`.
- `targets`.
- `created_at`.

Catatan:

- Model ada di `models.py` dan migration, tetapi view aktif saat ini menyimpan ringkasan AI ke `Wishlist`, bukan ke `SavedSummary`.

### 7.6 Contact

Fungsi:

- Menyimpan feedback user dan balasan admin.

Field:

- `user`.
- `name`.
- `email`.
- `message`.
- `admin_reply`.
- `replied_by`.
- `replied_at`.
- `created_at`.

### 7.7 EmailOTP

Fungsi:

- Menyimpan kode OTP.

Field:

- `user`.
- `otp`.
- `created_at`.

Catatan:

- Model tersedia, namun alur register aktif belum memakai OTP sebagai proses wajib.

## 8. Admin Panel

File: `main/admin.py`

Model yang didaftarkan:

- Wishlist.
- LoginHistory.
- SearchHistory.
- AIRecommendation.
- Contact.

Contact memiliki konfigurasi admin khusus:

- `list_display`: name, email, user, created_at, replied_at.
- `search_fields`: name, email, message, admin_reply.
- `list_filter`: created_at, replied_at.
- `readonly_fields`: created_at.

## 9. JavaScript Frontend

File: `main/static/js/app.js`

Fungsi utama:

- `getCsrf()`: mengambil CSRF token dari cookie.
- `apiFetch()`: wrapper fetch dengan CSRF dan JSON header.
- `openBookModal(book)`: membuka modal detail buku.
- `closeBookModal()`: menutup modal buku.
- `openLoginModal()`: membuka modal login required.
- `closeLoginModal()`: menutup modal login required.
- `hydrateBookDetail(book, requestId)`: mengambil detail tambahan dari backend.
- `toggleFavoriteFromModal()`: menambah atau menghapus favorit.
- `renderBooks(container, books, showRank)`: render card buku.
- `formatLanguage(language)`: format bahasa di frontend.
- OTP auto-next input.

## 10. Alur Sistem

### 10.1 Alur Register dan Login

1. User membuka halaman register.
2. User mengisi username, email, password, dan konfirmasi password.
3. Sistem memvalidasi field, email unik, username unik, dan konfirmasi password.
4. Akun dibuat.
5. User diarahkan ke login.
6. User login dengan username dan password.
7. Sistem membuat session login.
8. Sistem menyimpan riwayat login.
9. User masuk ke Home.

### 10.2 Alur Pencarian Buku

1. User mengetik judul buku pada search bar Home.
2. JavaScript menunggu 500 ms setelah input.
3. Frontend memanggil `/api/search/?q=...`.
4. Backend menyimpan riwayat pencarian jika user login.
5. Backend memanggil OpenLibrary API.
6. Backend mengolah data buku dan cover.
7. Frontend menampilkan card buku.
8. User klik card untuk membuka modal detail.
9. Jika detail kurang lengkap, frontend memanggil `/api/book-detail/`.

### 10.3 Alur Favorit

1. User membuka modal detail buku.
2. User klik "Tambah ke Favorit".
3. Frontend mengirim POST ke `/api/favorite/toggle/`.
4. Jika user belum login, sistem menampilkan modal login required.
5. Jika user login dan buku belum ada, buku disimpan ke `Wishlist`.
6. Jika buku sudah ada, data dihapus dari `Wishlist`.

### 10.4 Alur Buku Populer

1. Frontend memanggil `/api/popular/`.
2. Backend menghitung jumlah wishlist per buku.
3. Buku diurutkan dari yang paling banyak disimpan.
4. Frontend menampilkan buku populer.

### 10.5 Alur Ringkasan AI

1. User login membuka halaman Ringkasan AI.
2. User memasukkan judul buku.
3. Backend mencari metadata buku di OpenLibrary.
4. Backend membuat prompt ringkasan.
5. Backend mengirim prompt ke Groq API.
6. Groq mengembalikan JSON berisi ringkasan, poin penting, dan target pembaca.
7. Backend parsing JSON.
8. Backend menyimpan hasil ke `Wishlist`.
9. Frontend menampilkan cover, ringkasan, poin penting, dan target pembaca.

### 10.6 Alur Feedback

1. User login membuka halaman Feedback.
2. User mengisi nama dan pesan maksimal 200 karakter.
3. Sistem menyimpan feedback ke `Contact`.
4. User diarahkan ke halaman Pesan Saya.
5. Admin membuka halaman Pesan.
6. Admin menulis balasan atau menghapus pesan.
7. User bisa melihat balasan admin di Pesan Saya.

## 11. Fitur Aktif dan Fitur yang Masih Potensial

Fitur aktif:

- Home.
- Search buku dari OpenLibrary.
- Detail buku modal.
- Login dan register manual.
- Google login link melalui allauth.
- Logout.
- Wishlist/favorit.
- Buku populer berdasarkan wishlist.
- Ringkasan AI dengan Groq.
- Penyimpanan ringkasan AI ke wishlist.
- Feedback user.
- Pesan dan balasan admin.
- Riwayat login.
- Riwayat pencarian.
- Admin panel.
- Responsive design.

Fitur tersedia tetapi belum sepenuhnya menjadi alur aktif:

- OTP verifikasi email.
- Model `AIRecommendation`.
- Model `SavedSummary`.
- DeepSeek AI Search sesuai teks About.
- Label Gemini pada tampilan Ringkasan AI.
- Lupa password.

## 12. Kelebihan Sistem

- Memanfaatkan API eksternal sehingga data buku tidak perlu dimasukkan manual.
- Memiliki fitur AI yang memberi nilai tambah berupa ringkasan dan poin penting.
- Terdapat autentikasi user.
- Favorit tersimpan per user.
- Buku populer dihitung dari aktivitas pengguna.
- Tersedia feedback dan balasan admin.
- UI konsisten dengan warna, font, card, dan modal.
- Ada test untuk autentikasi dan visibilitas feedback.

## 13. Catatan untuk Penulisan Jurnal

Poin yang cocok dimasukkan ke jurnal:

- Latar belakang: banyak pembaca kesulitan memilih buku yang sesuai minat, sehingga diperlukan website rekomendasi dan ringkasan buku.
- Tujuan: membangun website BookAI untuk pencarian buku, penyimpanan favorit, dan ringkasan AI.
- Metode: pengembangan web menggunakan Django, integrasi OpenLibrary API, integrasi Groq AI, dan database MySQL.
- Hasil: sistem mampu menampilkan buku, detail buku, buku populer, menyimpan favorit, menghasilkan ringkasan AI, dan mengelola feedback.
- Pengujian: pengujian autentikasi, register, login, validasi duplicate username, dan akses feedback.
- Kesimpulan: BookAI dapat membantu user menemukan buku dan memahami isi buku secara lebih cepat melalui ringkasan AI.

## 14. Prompt untuk Membuat Jurnal

Prompt berikut bisa dipakai untuk meminta AI membuat draf jurnal berdasarkan project ini:

```text
Buatkan jurnal ilmiah berbahasa Indonesia tentang website BookAI, yaitu website rekomendasi dan ringkasan buku berbasis Django. Susun dengan format: judul, abstrak, kata kunci, pendahuluan, metode penelitian/pengembangan, perancangan sistem, implementasi, hasil dan pembahasan, pengujian, kesimpulan, dan daftar pustaka.

Detail sistem:
- Nama aplikasi: BookAI.
- Tujuan: membantu pengguna mencari buku, melihat detail buku, menyimpan favorit, melihat buku populer, membuat ringkasan buku dengan AI, dan mengirim feedback kepada admin.
- Backend: Python Django 4.2.23.
- Frontend: HTML, CSS custom, JavaScript vanilla, Django Template Language.
- Database: MySQL dengan database db_buku.
- Autentikasi: Django Authentication dan django-allauth untuk Google login.
- API buku: OpenLibrary API untuk pencarian buku, metadata, dan cover.
- AI: Groq API model llama-3.3-70b-versatile untuk membuat ringkasan buku dalam Bahasa Indonesia.
- Fitur utama: register, login, logout, search buku, modal detail buku, favorit/wishlist, buku populer berdasarkan jumlah wishlist, ringkasan AI, feedback user, pesan dan balasan admin, riwayat login, riwayat pencarian, admin panel.
- Desain UI: warna utama ungu #6C3FC5, background lavender #EEEAF8, card putih, font Playfair Display untuk judul dan DM Sans untuk isi.
- Model database: Wishlist, SearchHistory, AIRecommendation, LoginHistory, SavedSummary, Contact, EmailOTP.
- Catatan: OTP, AIRecommendation, SavedSummary, DeepSeek text, label Gemini, dan lupa password masih tersedia/tertera tetapi belum menjadi fitur aktif utama.

Tuliskan dengan gaya akademik, jelas, lengkap, dan cocok untuk laporan/jurnal proyek web. Jangan menyebutkan API key, password, atau credential rahasia.
```

## 15. Prompt AI Ringkasan Buku dalam Sistem

Prompt internal yang dipakai fitur Ringkasan AI:

```text
Buat ringkasan buku "{book_title}" dalam Bahasa Indonesia.

Berikan output JSON VALID tanpa markdown.

Format:

{
    "ringkasan": "ringkasan minimal 150 kata",
    "poin_penting": [
        "poin 1",
        "poin 2",
        "poin 3",
        "poin 4"
    ],
    "cocok_untuk": [
        "Mahasiswa",
        "Karyawan",
        "Pengusaha"
    ]
}
```

## 16. Prompt untuk Membuat Laporan Proyek Akhir

Prompt ini disusun khusus mengikuti format dosen untuk laporan mata kuliah Pemrograman Web Lanjut. Gunakan prompt ini jika ingin meminta AI membantu membuat draf laporan lengkap berdasarkan proyek BookAI.

```text
Tolong buatkan LAPORAN PROYEK AKHIR untuk mata kuliah Pemrograman Web Lanjut dengan bahasa Indonesia yang rapi, natural, dan terasa seperti tulisan mahasiswa. Jangan gunakan bahasa yang terlalu kaku, berulang, atau terlalu terlihat seperti hasil AI. Tulis dengan gaya akademik sederhana, jelas, dan manusiawi.

Data proyek:
- Judul proyek: BookAI - Website Rekomendasi dan Ringkasan Buku Berbasis Web
- Jenis sistem: website rekomendasi buku dan ringkasan buku berbasis AI
- Tujuan utama: membantu pengguna mencari buku, melihat detail buku, menyimpan buku favorit, melihat buku populer, membuat ringkasan buku dengan AI, serta mengirim feedback kepada admin
- Backend: Python Django 4.2.23
- Frontend: HTML, CSS custom, JavaScript vanilla, Django Template Language
- Database: MySQL dengan nama database db_buku
- Autentikasi: Django Authentication, session login, register manual, logout, dan dukungan django-allauth untuk Google login
- API eksternal: OpenLibrary API untuk pencarian buku, metadata buku, dan cover buku
- AI: Groq API dengan model llama-3.3-70b-versatile untuk membuat ringkasan buku dalam Bahasa Indonesia
- Hosting/deployment: VPS AnymHost dengan domain rekomendasibukuweb.my.id
- Akses server: ssh root@109.110.188.149
- Teknologi server: Ubuntu Server 20.04 LTS, Python 3.8, Virtual Environment (venv), Gunicorn, Nginx, systemd, socket .sock, DNS, domain, dan public IP
- Desain UI: warna utama ungu #6C3FC5, ungu muda #8B5CF6, background lavender #EEEAF8, card putih, font Playfair Display untuk judul, dan DM Sans untuk isi
- Fitur utama: login, register, logout, pencarian buku, detail buku dalam modal, favorit/wishlist, buku populer berdasarkan jumlah wishlist, ringkasan AI, feedback user, pesan dan balasan admin, riwayat login, riwayat pencarian, dan admin panel
- Model database: Wishlist, SearchHistory, AIRecommendation, LoginHistory, SavedSummary, Contact, EmailOTP
- Catatan fitur: OTP, SavedSummary, AIRecommendation, label Gemini, teks DeepSeek, dan lupa password masih ada di kode/tampilan, tetapi belum menjadi fitur aktif utama. Jelaskan dengan hati-hati sebagai fitur yang tersedia atau potensi pengembangan, bukan sebagai fitur utama yang sudah berjalan penuh.
- Autentikasi yang benar pada sistem ini adalah session-based authentication dari Django. Jika bagian teori meminta JWT Authentication, jelaskan JWT sebagai konsep autentikasi modern secara umum, lalu terangkan bahwa implementasi proyek ini memakai Django session authentication.

Susun laporan dengan struktur berikut:

HALAMAN JUDUL
Isi bagian ini dengan format:
- Judul Proyek
- Nama Mahasiswa: [isi nama]
- NIM: [isi NIM]
- Program Studi: [isi program studi]
- Mata Kuliah: Pemrograman Web Lanjut
- Dosen Pengampu: [isi nama dosen]
- Tahun Akademik: [isi tahun akademik]

ABSTRAK
Tulis abstrak sepanjang 150 sampai 250 kata. Abstrak harus memuat:
- latar belakang masalah
- tujuan penelitian/pengembangan
- metode yang digunakan
- hasil utama
- kesimpulan
Gunakan bahasa yang padat tetapi tetap mudah dipahami. Setelah abstrak, tuliskan maksimal 5 kata kunci secara berurutan.

BAB I PENDAHULUAN
1.1 Latar Belakang
Jelaskan masalah yang melatarbelakangi proyek BookAI, misalnya pengguna sering kesulitan menemukan buku yang sesuai minat, pencarian buku masih membutuhkan waktu, dan tidak semua pengguna sempat membaca sinopsis panjang. Jelaskan dampak masalah tersebut dan mengapa solusi berbasis web dengan API buku dan AI ringkasan dibutuhkan.

1.2 Rumusan Masalah
Buat rumusan masalah yang sesuai dengan BookAI, misalnya:
- Bagaimana merancang website rekomendasi buku berbasis web?
- Bagaimana mengimplementasikan pencarian buku menggunakan OpenLibrary API?
- Bagaimana mengimplementasikan autentikasi pengguna pada sistem BookAI?
- Bagaimana membuat fitur favorit dan buku populer berdasarkan aktivitas pengguna?
- Bagaimana mengintegrasikan AI untuk membuat ringkasan buku?
- Bagaimana menguji fungsionalitas sistem yang dibangun?

1.3 Tujuan Penelitian
Jelaskan tujuan pengembangan sistem, yaitu membangun website BookAI yang mampu melakukan pencarian buku, menampilkan detail buku, menyimpan favorit, menampilkan buku populer, membuat ringkasan AI, dan mengelola feedback pengguna.

1.4 Manfaat Penelitian
Jelaskan manfaat:
- bagi pengguna: membantu menemukan buku dan memahami isi buku lebih cepat
- bagi institusi: menjadi contoh penerapan pemrograman web lanjut dengan API dan AI
- bagi pengembangan ilmu: menjadi referensi pengembangan web berbasis Django, API eksternal, database, dan AI

BAB II TINJAUAN PUSTAKA
2.1 Penelitian Terdahulu
Buat tabel penelitian terdahulu minimal 5 jurnal dengan kolom:
- Penulis
- Tahun
- Judul
- Metode
- Hasil
- Gap Penelitian
Gunakan jurnal yang relevan dengan sistem rekomendasi buku, sistem informasi berbasis web, integrasi API, penerapan AI/NLP, dan pengujian sistem. Jangan mengarang referensi. Jika referensi asli belum tersedia, beri placeholder yang jelas seperti [isi referensi jurnal 1 dari Mendeley].

2.2 Landasan Teori
Jelaskan teori yang sesuai dengan proyek:
- Sistem Informasi
- Website dan Aplikasi Web
- Web Framework
- Django
- Database dan MySQL
- REST API
- OpenLibrary API
- Artificial Intelligence untuk ringkasan teks
- Autentikasi pengguna, termasuk session authentication dan konsep JWT Authentication
- Hosting dan VPS
- Ubuntu Server
- Nginx
- Gunicorn
- Virtual Environment (venv)
- Systemd Service
- Socket .sock
- Domain dan DNS
- SSL/HTTPS
- Firewall
- UML
- Use Case Diagram
- Activity Diagram
- Sequence Diagram
- Class Diagram
- Entity Relationship Diagram
- Pengujian Sistem
- Black Box Testing
- User Acceptance Test dengan skala Likert

2.3 Kerangka Pemikiran
Buat penjelasan dan diagram alur penelitian dalam bentuk teks. Alurnya:
Identifikasi masalah -> pengumpulan kebutuhan -> perancangan sistem -> implementasi Django, database, API, dan AI -> pengujian sistem -> evaluasi hasil -> kesimpulan.

BAB III METODOLOGI PENELITIAN
3.1 Metode Penelitian
Gunakan metode Prototype atau Waterfall. Pilih salah satu yang paling cocok. Jika memakai Prototype, jelaskan bahwa sistem dikembangkan melalui analisis kebutuhan, desain awal, implementasi, evaluasi, perbaikan, dan pengujian.

3.2 Tahapan Penelitian
Buat tahapan penelitian dalam bentuk penjelasan dan diagram teks. Tahapan:
- identifikasi masalah
- studi pustaka
- analisis kebutuhan
- perancangan sistem
- implementasi
- deployment ke VPS AnymHost
- pengujian
- evaluasi
- penyusunan laporan

3.3 Analisis Kebutuhan
Pisahkan menjadi:

Kebutuhan Fungsional:
- user dapat register
- user dapat login
- user dapat logout
- user dapat mencari buku
- user dapat melihat detail buku
- user dapat menyimpan dan menghapus buku favorit
- user dapat melihat daftar favorit
- user dapat melihat buku populer
- user dapat membuat ringkasan buku dengan AI
- user dapat mengirim feedback
- user dapat melihat balasan admin
- admin dapat melihat semua pesan feedback
- admin dapat membalas feedback
- admin dapat menghapus feedback
- sistem dapat menyimpan riwayat login
- sistem dapat menyimpan riwayat pencarian

Kebutuhan Non Fungsional:
- Security: login, CSRF token, pemisahan akses user dan admin, perlindungan data rahasia
- Performance: pencarian buku menggunakan API dan limit hasil
- Availability: sistem dapat dijalankan melalui server Django dan database MySQL
- Usability: tampilan sederhana, responsif, warna konsisten, dan mudah dipahami

3.4 Perancangan Sistem
Jelaskan rancangan berikut berdasarkan BookAI:
- Use Case Diagram: aktor user dan admin
- Activity Diagram: alur login, pencarian buku, tambah favorit, ringkasan AI, dan feedback
- Sequence Diagram: interaksi user, frontend, backend Django, database, OpenLibrary API, dan Groq API
- Class Diagram: User, Wishlist, SearchHistory, LoginHistory, Contact, EmailOTP, SavedSummary, AIRecommendation
- ERD Database: relasi User dengan Wishlist, SearchHistory, LoginHistory, Contact, EmailOTP, SavedSummary, dan AIRecommendation
- Arsitektur Sistem: browser -> Django views -> database MySQL -> OpenLibrary API/Groq API -> response ke frontend

BAB IV HASIL DAN PEMBAHASAN
4.1 Implementasi Sistem
Jelaskan:
- framework yang digunakan yaitu Django
- bahasa pemrograman Python, HTML, CSS, dan JavaScript
- database MySQL
- integrasi OpenLibrary API
- integrasi Groq AI
- penggunaan Django Template
- penggunaan static files CSS dan JS
- deployment menggunakan VPS AnymHost
- Ubuntu Server 20.04 LTS
- Python 3.8 dan venv
- Gunicorn sebagai application server
- Nginx sebagai web server
- systemd service untuk menjalankan Gunicorn otomatis
- socket .sock sebagai penghubung Nginx dan Gunicorn
- domain rekomendasibukuweb.my.id dan DNS
- SSH access, root access, public IP, firewall, SSL/HTTPS, monitoring, backup, file management, restart service, dan custom configuration

Tambahkan subbagian "Implementasi Hosting dan Deployment" yang menjelaskan:
- aplikasi sudah di-hosting menggunakan AnymHost
- domain yang digunakan adalah rekomendasibukuweb.my.id
- server diakses melalui ssh root@109.110.188.149
- alur deployment dari upload project, install dependency, konfigurasi database, migrasi, collectstatic, konfigurasi Gunicorn, systemd, Nginx, DNS, sampai website dapat diakses
- diagram alur request: Browser -> Domain -> DNS -> VPS -> Nginx -> Gunicorn socket -> Django -> Database/API/AI -> Browser
- alasan VPS lebih cocok dibanding shared hosting untuk aplikasi Django

4.2 Tampilan Sistem
Jelaskan screenshot yang perlu dimasukkan:
- halaman login
- halaman register
- halaman home sebagai dashboard utama
- pencarian buku
- modal detail buku
- halaman favorit
- halaman buku populer
- halaman ringkasan AI
- halaman feedback
- halaman pesan user
- halaman pesan admin
- halaman about
Jika dosen meminta "Dashboard", gunakan halaman Home sebagai dashboard utama. Jika dosen meminta "Laporan", jelaskan bahwa sistem ini tidak memiliki modul laporan cetak, tetapi memiliki halaman daftar favorit, pesan, dan riwayat data yang tersimpan di database.

4.3 Pengujian Sistem
Buat Black Box Testing dalam tabel dengan kolom:
- Skenario
- Input
- Output yang diharapkan
- Hasil
Buat minimal skenario untuk:
- register berhasil
- register gagal karena username sama
- login berhasil
- login gagal
- pencarian buku
- membuka detail buku
- tambah favorit
- hapus favorit
- membuat ringkasan AI
- kirim feedback
- admin membalas pesan
- admin menghapus pesan

Buat juga bagian User Acceptance Test atau UAT.
Gunakan minimal 10 responden dengan skala Likert 1 sampai 5:
1 = sangat tidak setuju
2 = tidak setuju
3 = netral
4 = setuju
5 = sangat setuju
Buat contoh tabel pertanyaan UAT yang menilai kemudahan penggunaan, kejelasan tampilan, kecepatan pencarian, manfaat ringkasan AI, kemudahan menyimpan favorit, dan kepuasan umum.

Pengujian performa opsional:
Jika data asli belum ada, buat format tabel untuk response time dan load testing, tetapi jangan mengarang hasil final. Beri keterangan bahwa hasil perlu diisi setelah pengujian dilakukan.

4.4 Pembahasan
Bahas:
- apakah tujuan sistem tercapai
- keunggulan BookAI
- keterbatasan sistem
- fitur yang belum aktif penuh
- perbandingan dengan penelitian sebelumnya
- peluang pengembangan berikutnya

BAB V PENUTUP
5.1 Kesimpulan
Tulis kesimpulan yang menjawab tujuan penelitian. Jelaskan bahwa BookAI berhasil menyediakan pencarian buku, detail buku, favorit, buku populer, ringkasan AI, dan feedback admin-user.

5.2 Saran
Berikan saran:
- mengaktifkan OTP secara penuh
- memperbaiki label AI agar konsisten dengan Groq
- menambahkan reset password
- menambahkan rekomendasi personal berdasarkan riwayat
- menambahkan rating dan review buku
- menambahkan export laporan
- meningkatkan keamanan credential dengan environment variable
- melakukan pengujian performa lebih lanjut

DAFTAR PUSTAKA
Buat arahan daftar pustaka menggunakan Mendeley. Ketentuan:
- minimal 25 referensi
- minimal 80% jurnal
- minimal 5 tahun terakhir
- gunakan gaya sitasi sesuai ketentuan kampus
Jangan mengarang data jurnal. Jika belum diberi daftar referensi, buat bagian daftar pustaka sebagai placeholder dan beri catatan bahwa referensi harus diisi dari Mendeley.

LAMPIRAN
Buat daftar lampiran:
- Source Code Repository GitHub/GitLab
- Dokumentasi Pengembangan
- Hasil Pengujian
- Manual Book Pengguna
- Link Demo Sistem
- Screenshot Sistem
- Diagram UML dan ERD

Ketentuan gaya bahasa:
- Gunakan bahasa Indonesia yang natural dan mudah dibaca.
- Jangan terlalu sering memakai kalimat seperti "penelitian ini bertujuan" secara berulang.
- Hindari kalimat yang terlalu umum dan kosong.
- Hubungkan setiap pembahasan dengan sistem BookAI.
- Jangan mengklaim fitur yang belum benar-benar aktif sebagai fitur utama.
- Jangan menuliskan API key, password, atau credential rahasia.
- Buat laporan lengkap, sistematis, dan siap dirapikan ke format Word.
```

## 17. Analisis Hosting dan Deployment AnymHost

Website BookAI tidak hanya berjalan di komputer lokal, tetapi sudah di-deploy menggunakan layanan hosting/VPS AnymHost dengan domain:

```text
rekomendasibukuweb.my.id
```

Akses server dilakukan melalui SSH:

```text
ssh root@109.110.188.149
```

Catatan: bagian ini disusun berdasarkan informasi deployment yang diberikan. Detail tertentu seperti database produksi, konfigurasi firewall, SSL, backup, dan monitoring tetap perlu dicek langsung dari panel AnymHost atau konfigurasi server jika ingin ditulis sebagai hasil verifikasi penuh.

### 17.1 Gambaran Infrastruktur Server

Infrastruktur deployment BookAI menggunakan pola umum deployment Django di VPS:

```text
Browser pengguna
-> Domain rekomendasibukuweb.my.id
-> DNS mengarah ke Public IP VPS
-> Nginx menerima request HTTP/HTTPS
-> Nginx meneruskan request ke Gunicorn melalui socket
-> Gunicorn menjalankan aplikasi Django
-> Django memproses view, template, static, database, OpenLibrary API, dan Groq AI
-> Response dikirim kembali ke browser pengguna
```

Dengan arsitektur ini, Nginx berperan sebagai gerbang web server, sedangkan Gunicorn berperan sebagai application server yang menjalankan kode Python/Django.

### 17.2 VPS AnymHost

VPS atau Virtual Private Server adalah server virtual yang memberikan kontrol lebih besar kepada pengembang dibanding shared hosting. Pada deployment BookAI, VPS digunakan karena Django membutuhkan konfigurasi server yang lebih fleksibel, seperti instalasi Python, virtual environment, Gunicorn, Nginx, systemd service, domain, dan konfigurasi static files.

Manfaat VPS untuk BookAI:

- Pengembang dapat mengakses server melalui SSH.
- Pengembang memiliki root access untuk instalasi dan konfigurasi layanan.
- Server memiliki public IP address sendiri.
- Konfigurasi Nginx, Gunicorn, firewall, dan service dapat disesuaikan.
- Cocok untuk aplikasi Django yang membutuhkan proses backend Python berjalan terus-menerus.

### 17.3 Ubuntu Server 20.04 LTS

Server menggunakan Ubuntu Server 20.04 LTS. Ubuntu Server adalah sistem operasi berbasis Linux yang umum digunakan untuk menjalankan aplikasi web. Versi LTS atau Long Term Support dipilih karena lebih stabil dan mendapatkan dukungan keamanan dalam jangka panjang.

Fungsi Ubuntu Server dalam deployment BookAI:

- Menjadi sistem operasi utama VPS.
- Menyediakan lingkungan untuk menjalankan Python, Django, Gunicorn, dan Nginx.
- Menyediakan command line untuk konfigurasi server.
- Mendukung systemd untuk menjalankan service secara otomatis.

Alasan Ubuntu Server cocok digunakan:

- Stabil untuk aplikasi web.
- Banyak dokumentasi deployment Django tersedia untuk Ubuntu.
- Mudah dikonfigurasi melalui SSH.
- Kompatibel dengan Nginx, Gunicorn, Python, dan database.

### 17.4 Python 3.8

Python 3.8 digunakan sebagai bahasa pemrograman utama pada sisi server. Django berjalan di atas Python, sehingga seluruh logika backend seperti autentikasi, pencarian buku, favorit, feedback, dan ringkasan AI diproses oleh kode Python.

Fungsi Python dalam BookAI:

- Menjalankan framework Django.
- Memproses request dari user.
- Menghubungkan aplikasi dengan database.
- Mengambil data dari OpenLibrary API.
- Mengirim prompt ke Groq AI.

### 17.5 Django

Django adalah web framework Python yang digunakan sebagai fondasi aplikasi BookAI. Django mengatur routing URL, view, model database, template HTML, autentikasi user, admin panel, dan middleware keamanan seperti CSRF.

Peran Django pada deployment:

- Menjalankan logika backend aplikasi.
- Mengatur halaman seperti Home, Login, Register, Favorites, Ringkasan AI, Feedback, dan Pesan.
- Menghubungkan model database dengan data aplikasi.
- Menghasilkan halaman HTML yang dikirim ke browser.

### 17.6 Gunicorn

Gunicorn atau Green Unicorn adalah application server WSGI yang digunakan untuk menjalankan aplikasi Django di server produksi. Django sebenarnya memiliki development server bawaan, tetapi server bawaan tersebut tidak disarankan untuk produksi. Karena itu, Gunicorn digunakan agar aplikasi Django dapat berjalan lebih stabil di VPS.

Fungsi Gunicorn:

- Menjalankan file WSGI Django.
- Menerima request dari Nginx.
- Menghubungkan web server dengan aplikasi Python.
- Menjalankan proses worker untuk memproses request pengguna.

Hubungan Gunicorn dengan Django:

```text
Nginx -> Gunicorn -> Django WSGI -> Views Django -> Response
```

Dengan Gunicorn, aplikasi Django dapat melayani request pengguna secara lebih layak untuk lingkungan hosting.

### 17.7 Nginx

Nginx adalah web server yang berada di depan Gunicorn. Nginx menerima request dari browser pengguna melalui domain, kemudian meneruskan request dinamis ke Gunicorn. Selain itu, Nginx juga biasanya digunakan untuk melayani file static seperti CSS, JavaScript, gambar, dan file media.

Fungsi Nginx:

- Menerima request HTTP/HTTPS dari pengguna.
- Mengarahkan request ke Gunicorn.
- Melayani file static agar lebih cepat.
- Mengatur domain dan konfigurasi server block.
- Dapat digunakan untuk konfigurasi SSL/HTTPS.

Cara kerja sederhana:

```text
Pengguna membuka rekomendasibukuweb.my.id
-> Nginx menerima request
-> Jika request static, Nginx dapat langsung mengirim file
-> Jika request halaman Django, Nginx meneruskan ke Gunicorn
-> Gunicorn meminta Django memproses request
-> Hasil dikirim kembali melalui Nginx ke browser
```

### 17.8 Virtual Environment (venv)

Virtual environment atau `venv` digunakan untuk memisahkan package Python aplikasi BookAI dari package Python sistem server. Dengan venv, dependency seperti Django, requests, groq, mysqlclient, dan package lain dapat dikelola khusus untuk proyek ini.

Manfaat venv:

- Dependency proyek lebih rapi.
- Menghindari bentrok package antar aplikasi.
- Memudahkan instalasi dari `requirements.txt`.
- Membuat deployment lebih terkontrol.

### 17.9 Systemd Service

Systemd digunakan untuk menjalankan Gunicorn sebagai service di Ubuntu Server. Dengan systemd, Gunicorn dapat berjalan otomatis saat server dinyalakan dan dapat dikelola menggunakan perintah seperti start, stop, restart, dan status.

Fungsi systemd service:

- Menjalankan Gunicorn di background.
- Menghidupkan Gunicorn otomatis saat server reboot.
- Memudahkan restart aplikasi setelah perubahan kode.
- Memantau status service Gunicorn.

Contoh konsep perintah:

```text
systemctl status gunicorn
systemctl restart gunicorn
```

### 17.10 Socket (.sock)

Socket `.sock` digunakan sebagai jalur komunikasi lokal antara Nginx dan Gunicorn. Daripada meneruskan request melalui port TCP publik, Nginx dapat meneruskan request ke file socket yang dibuat oleh Gunicorn.

Fungsi socket:

- Menghubungkan Nginx dan Gunicorn di server yang sama.
- Membuat komunikasi lokal lebih efisien.
- Mengurangi kebutuhan membuka port tambahan.
- Menjaga arsitektur deployment lebih rapi.

Alur socket:

```text
Nginx -> file gunicorn.sock -> Gunicorn -> Django
```

### 17.11 Database Produksi

Pada kode project lokal, konfigurasi Django mengarah ke MySQL dengan nama database `db_buku`. Pada instruksi hosting disebutkan SQLite/PostgreSQL perlu disesuaikan dengan database yang digunakan. Untuk laporan, bagian database sebaiknya ditulis sesuai kondisi produksi yang benar.

Jika server produksi memakai MySQL seperti konfigurasi project:

- Database digunakan untuk menyimpan user, wishlist, riwayat pencarian, riwayat login, feedback, dan data ringkasan AI.
- MySQL cocok untuk aplikasi web karena mendukung relasi data dan query yang stabil.

Jika server produksi memakai SQLite:

- SQLite menyimpan data dalam satu file database.
- Cocok untuk deployment kecil atau tahap awal.
- Namun untuk produksi jangka panjang, MySQL atau PostgreSQL lebih disarankan.

Jika server produksi memakai PostgreSQL:

- PostgreSQL cocok untuk aplikasi produksi karena kuat, stabil, dan mendukung fitur database yang lengkap.

Untuk laporan BookAI, gunakan kalimat aman berikut jika belum mengecek database server:

```text
Pada pengembangan lokal, sistem dikonfigurasi menggunakan MySQL dengan database db_buku. Pada deployment server, database perlu disesuaikan dengan konfigurasi produksi yang digunakan, baik MySQL, SQLite, maupun PostgreSQL.
```

### 17.12 Domain dan DNS

Domain `rekomendasibukuweb.my.id` digunakan agar pengguna dapat mengakses aplikasi menggunakan nama yang mudah diingat, bukan alamat IP server. DNS berfungsi menerjemahkan domain tersebut ke public IP VPS AnymHost.

Fungsi DNS:

- Menghubungkan domain dengan IP server.
- Membuat website dapat diakses melalui alamat domain.
- Memudahkan pengguna karena tidak perlu mengetik IP.

Contoh konsep:

```text
rekomendasibukuweb.my.id -> DNS A Record -> 109.110.188.149 -> VPS AnymHost
```

### 17.13 SSL/HTTPS

SSL/HTTPS digunakan untuk mengenkripsi komunikasi antara browser pengguna dan server. Dengan HTTPS, data login dan aktivitas pengguna lebih aman ketika dikirim melalui internet.

Manfaat HTTPS:

- Mengamankan data user.
- Meningkatkan kepercayaan pengguna.
- Menghindari label "Not Secure" pada browser.
- Lebih layak untuk website yang memiliki fitur login.

Jika SSL sudah aktif, laporan dapat menulis bahwa domain sudah diamankan dengan HTTPS. Jika belum dicek, tulis sebagai fitur yang disarankan atau tersedia pada konfigurasi hosting.

### 17.14 Firewall

Firewall digunakan untuk mengatur port yang boleh diakses dari luar server. Pada deployment Django dengan Nginx, port umum yang dibuka biasanya:

- Port 22 untuk SSH.
- Port 80 untuk HTTP.
- Port 443 untuk HTTPS.

Gunicorn biasanya tidak perlu dibuka ke publik karena request cukup diteruskan dari Nginx melalui socket.

### 17.15 Monitoring Resource

Monitoring resource digunakan untuk memantau penggunaan CPU, RAM, storage, dan traffic server. Pada VPS, monitoring penting agar pengembang mengetahui apakah server masih cukup kuat menjalankan aplikasi.

Manfaat monitoring:

- Melihat beban server.
- Mendeteksi aplikasi yang terlalu berat.
- Membantu menentukan kebutuhan upgrade VPS.
- Memantau stabilitas layanan.

### 17.16 Backup

Backup berfungsi menyimpan salinan data project dan database agar dapat dipulihkan jika terjadi kerusakan server atau kesalahan konfigurasi. Jika AnymHost menyediakan fitur backup, fitur tersebut dapat dimanfaatkan untuk menjaga keamanan data aplikasi.

Data yang sebaiknya dibackup:

- Source code aplikasi.
- File `.env`.
- Database.
- File media/static jika ada upload.
- Konfigurasi Nginx dan systemd.

### 17.17 File Management, Restart Service, dan Custom Configuration

Pada VPS, pengembang dapat mengelola file project melalui SSH, SFTP, Git, atau file manager yang tersedia dari panel hosting. Setelah kode diperbarui, service Gunicorn biasanya perlu di-restart agar perubahan backend terbaca.

Contoh aktivitas deployment:

- Upload atau pull source code.
- Install dependency di venv.
- Jalankan migrasi database.
- Collect static files.
- Restart Gunicorn.
- Reload Nginx jika konfigurasi web server berubah.

VPS juga mendukung custom configuration, seperti pengaturan domain, server block Nginx, worker Gunicorn, environment variable, dan firewall.

### 17.18 Proses Deployment BookAI

Proses deployment aplikasi BookAI secara umum:

1. Developer menyiapkan source code Django di komputer lokal.
2. Source code di-upload ke VPS melalui Git, SFTP, atau SCP.
3. Developer login ke server menggunakan SSH:

```text
ssh root@109.110.188.149
```

4. Server menyiapkan Python 3.8 dan virtual environment.
5. Dependency diinstall dari `requirements.txt`.
6. File konfigurasi seperti `.env`, database, dan static path disiapkan.
7. Migrasi database dijalankan.
8. Static files dikumpulkan agar dapat dilayani Nginx.
9. Gunicorn dikonfigurasi untuk menjalankan aplikasi Django melalui WSGI.
10. Systemd service dibuat agar Gunicorn berjalan otomatis.
11. Socket `.sock` dibuat sebagai penghubung Gunicorn dan Nginx.
12. Nginx dikonfigurasi untuk domain `rekomendasibukuweb.my.id`.
13. DNS domain diarahkan ke public IP VPS.
14. SSL/HTTPS dikonfigurasi jika digunakan.
15. User dapat membuka website melalui browser.

### 17.19 Diagram Alur Request

Diagram sederhana proses request:

```text
Pengguna
  |
  v
Browser membuka rekomendasibukuweb.my.id
  |
  v
DNS mengarahkan domain ke IP VPS 109.110.188.149
  |
  v
Nginx menerima request HTTP/HTTPS
  |
  v
Nginx meneruskan request ke Gunicorn melalui gunicorn.sock
  |
  v
Gunicorn menjalankan aplikasi Django
  |
  v
Django memproses URL, View, Model, Template, Database, API, dan AI
  |
  v
Response HTML/JSON dikirim kembali ke Nginx
  |
  v
Browser menampilkan halaman BookAI
```

### 17.20 Alasan VPS Lebih Cocok Dibanding Shared Hosting

VPS lebih cocok untuk deployment Django dibanding shared hosting karena:

- Django membutuhkan application server seperti Gunicorn.
- Deployment membutuhkan konfigurasi Nginx.
- Aplikasi membutuhkan virtual environment Python.
- Pengembang perlu menjalankan migrasi database dan collectstatic.
- Pengembang membutuhkan akses SSH dan root access.
- Konfigurasi service seperti systemd biasanya tidak tersedia bebas pada shared hosting.
- VPS lebih fleksibel untuk integrasi API, AI, dan konfigurasi keamanan.

Shared hosting lebih cocok untuk website statis atau PHP sederhana. Untuk aplikasi Django yang memiliki backend Python, database, AI, dan service khusus, VPS menjadi pilihan yang lebih tepat.

### 17.21 Kesimpulan Hosting

Penggunaan AnymHost sebagai media deployment BookAI memberikan fleksibilitas yang baik untuk menjalankan aplikasi Django. Dengan VPS, aplikasi dapat dikonfigurasi menggunakan Ubuntu Server 20.04 LTS, Python 3.8, virtual environment, Gunicorn, Nginx, systemd, socket, database, dan domain `rekomendasibukuweb.my.id`.

Arsitektur ini membuat BookAI dapat diakses oleh pengguna melalui internet, tidak hanya berjalan di komputer lokal. Nginx menangani request dari pengguna, Gunicorn menjalankan aplikasi Django, dan database menyimpan data sistem. Dengan dukungan domain, DNS, SSH, root access, serta kemungkinan penggunaan SSL dan firewall, AnymHost dapat menjadi pilihan yang sesuai untuk deployment aplikasi Django pada proyek akhir.
