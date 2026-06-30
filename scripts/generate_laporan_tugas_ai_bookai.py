from pathlib import Path
from html import escape, unescape
import json
from zipfile import ZipFile, ZIP_DEFLATED


BASE_DIR = Path(__file__).resolve().parent.parent
MD_OUT = BASE_DIR / "LAPORAN_TUGAS_AI_BOOKAI.md"
DOCX_OUT = BASE_DIR / "Laporan_Tugas_AI_BookAI.docx"
REF_PATH = BASE_DIR / "references_crossref_raw.json"

SELECTED_DOIS = [
    "10.1016/j.knosys.2023.110335",
    "10.1145/3700890",
    "10.1109/access.2024.3368027",
    "10.1109/access.2022.3177610",
    "10.12962/j24068535.v22i1.a1193",
    "10.31586/ijmebac.2022.341",
    "10.1149/10701.15439ecst",
    "10.1016/j.nlp.2023.100048",
    "10.1016/j.nlp.2023.100020",
    "10.1016/j.aej.2023.01.008",
    "10.33795/jip.v10i4.5242",
    "10.11591/ijece.v12i2.pp1990-2000",
    "10.1088/1742-6596/2040/1/012044",
    "10.25181/rt.v1i1.2700",
    "10.33084/jsakti.v3i2.1932",
]


def load_refs():
    if not REF_PATH.exists():
        return []
    refs = json.loads(REF_PATH.read_text(encoding="utf-8"))
    by_doi = {
        str(item.get("DOI", "")).lower(): item
        for item in refs
        if item.get("DOI")
    }
    return [by_doi[doi] for doi in SELECTED_DOIS if doi in by_doi]


def first(item, key):
    value = item.get(key)
    if isinstance(value, list):
        return unescape(str(value[0])) if value else ""
    return unescape(str(value or ""))


def ref_year(item):
    parts = item.get("issued", {}).get("date-parts", [[""]])
    return str(parts[0][0]) if parts and parts[0] else ""


def ref_authors(item):
    authors = []
    for author in item.get("author") or []:
        family = author.get("family", "").strip()
        given = author.get("given", "").strip()
        if family and given:
            authors.append(f"{family}, {given}")
        elif family:
            authors.append(family)
        elif given:
            authors.append(given)
    return authors


def ref_cite(item):
    authors = ref_authors(item)
    year = ref_year(item)
    if not authors:
        title = first(item, "title").split(":")[0]
        return f"{title}, {year}"
    first_family = authors[0].split(",")[0]
    if len(authors) == 1:
        return f"{first_family}, {year}"
    if len(authors) == 2:
        second_family = authors[1].split(",")[0]
        return f"{first_family} dan {second_family}, {year}"
    return f"{first_family} et al., {year}"


def ref_apa(item):
    authors = ref_authors(item)
    if not authors:
        authors_text = "Tanpa penulis"
    elif len(authors) == 1:
        authors_text = authors[0]
    else:
        authors_text = ", ".join(authors[:-1]) + ", & " + authors[-1]
    title = first(item, "title")
    journal = first(item, "container-title")
    doi = str(item.get("DOI", "")).lower()
    url = f"https://doi.org/{doi}" if doi else item.get("URL", "")
    return f"{authors_text}. ({ref_year(item)}). {title}. {journal}. {url}"


refs = load_refs()
cite = {str(item.get("DOI", "")).lower(): ref_cite(item) for item in refs}


def c(doi):
    return cite.get(doi, "Referensi")


sections = [
    ("title", "LAPORAN TUGAS KECERDASAN BUATAN"),
    ("center", "BookAI: Website Rekomendasi dan Ringkasan Buku Berbasis Kecerdasan Buatan"),
    ("center", "Disusun oleh: [Isi Nama Mahasiswa]"),
    ("center", "NIM: [Isi NIM]"),
    ("center", "Program Studi: [Isi Program Studi]"),
    ("center", "Mata Kuliah: Kecerdasan Buatan"),
    ("center", "Dosen Pengampu: [Isi Nama Dosen]"),
    ("page", ""),
    ("h1", "ABSTRAK"),
    ("p", (
        "BookAI adalah aplikasi web yang dikembangkan untuk membantu pengguna mencari buku, melihat detail buku, "
        "menyimpan buku favorit, melihat buku populer, dan membuat ringkasan buku menggunakan kecerdasan buatan. "
        "Aplikasi ini dibangun dengan framework Django, database MySQL, OpenLibrary API sebagai sumber metadata buku, "
        "dan Groq API dengan model llama-3.3-70b-versatile untuk menghasilkan ringkasan dalam Bahasa Indonesia. "
        "Fokus AI pada proyek ini adalah pemanfaatan Large Language Model untuk tugas text summarization, sedangkan "
        "fitur rekomendasi populer dihitung dari agregasi data wishlist pengguna. Metode pengembangan dilakukan melalui "
        "analisis kebutuhan, perancangan alur sistem, implementasi backend dan frontend, integrasi API, serta pengujian "
        "black box. Hasil aplikasi menunjukkan bahwa BookAI dapat menjadi media sederhana untuk menemukan buku dan "
        "memahami gambaran isi buku secara lebih cepat."
    )),
    ("p", "Kata kunci: BookAI, Kecerdasan Buatan, Large Language Model, Ringkasan Buku, Sistem Rekomendasi, Django."),
    ("page", ""),
    ("h1", "BAB I PENDAHULUAN"),
    ("h2", "1.1 Latar Belakang"),
    ("p", (
        "Jumlah buku digital dan metadata buku yang tersedia di internet terus bertambah. Kondisi ini memberi keuntungan "
        "karena pengguna memiliki lebih banyak pilihan bacaan, tetapi juga menimbulkan masalah baru, yaitu kesulitan "
        "menentukan buku yang sesuai dengan kebutuhan. Pengguna sering hanya melihat judul, cover, atau nama penulis, "
        "padahal informasi tersebut belum selalu cukup untuk memahami isi buku. Dalam konteks inilah sistem rekomendasi "
        "dan kecerdasan buatan dapat membantu proses pemilihan informasi."
    )),
    ("p", (
        "Penelitian sistem rekomendasi menunjukkan bahwa pendekatan rekomendasi dapat membantu pengguna menemukan item "
        "yang relevan dari kumpulan data yang besar. Perkembangan recommender system juga semakin luas, mulai dari "
        "content-based filtering, collaborative filtering, deep learning, sampai intent-aware recommender system "
        f"({c('10.1016/j.knosys.2023.110335')}; {c('10.1145/3700890')}). Pada bidang buku, collaborative filtering "
        f"dan item-based recommendation banyak digunakan karena data interaksi pengguna dapat dimanfaatkan untuk "
        f"menghasilkan rekomendasi yang lebih terarah ({c('10.31586/ijmebac.2022.341')}; {c('10.1149/10701.15439ecst')})."
    )),
    ("p", (
        "Selain rekomendasi, masalah lain yang sering dihadapi pembaca adalah kebutuhan memahami gambaran isi buku secara "
        "cepat. Large Language Model dan automatic text summarization dapat digunakan untuk membuat ringkasan yang lebih "
        "natural dibanding ringkasan berbasis pemotongan kalimat sederhana. Kajian tentang GPT dan model bahasa besar "
        f"menunjukkan bahwa LLM mampu digunakan untuk berbagai tugas bahasa alami ({c('10.1016/j.nlp.2023.100048')}; "
        f"{c('10.1016/j.nlp.2023.100020')}). Penelitian summarization juga mendukung penggunaan model deep learning "
        f"dan transformer untuk menghasilkan ringkasan abstraktif ({c('10.1016/j.aej.2023.01.008')}; "
        f"{c('10.33795/jip.v10i4.5242')})."
    )),
    ("p", (
        "Berdasarkan kebutuhan tersebut, proyek BookAI dikembangkan sebagai aplikasi berbasis kecerdasan buatan yang "
        "terhubung dengan website rekomendasi buku yang sudah ada pada project ini. BookAI tidak hanya menampilkan data "
        "buku dari OpenLibrary, tetapi juga menyediakan ringkasan AI, poin penting, target pembaca, wishlist, buku populer, "
        "feedback user, dan halaman pesan admin. Dengan demikian, laporan ini disusun agar sesuai dengan implementasi "
        "project BookAI, bukan hanya berisi teori umum tentang AI."
    )),
    ("h2", "1.2 Rumusan Masalah"),
    ("list", [
        "Bagaimana merancang aplikasi BookAI sebagai aplikasi berbasis kecerdasan buatan?",
        "Bagaimana mengintegrasikan OpenLibrary API sebagai sumber data buku?",
        "Bagaimana menerapkan Large Language Model untuk membuat ringkasan buku dalam Bahasa Indonesia?",
        "Bagaimana menjelaskan algoritma AI dan alur rekomendasi yang digunakan dalam project BookAI?",
        "Bagaimana hasil implementasi aplikasi BookAI dari sisi fitur dan pengujian?",
    ]),
    ("h2", "1.3 Tujuan"),
    ("list", [
        "Membangun aplikasi web yang membantu pengguna mencari dan menyimpan buku favorit.",
        "Mengimplementasikan fitur ringkasan AI menggunakan Groq API dan model llama-3.3-70b-versatile.",
        "Menyediakan fitur buku populer berdasarkan jumlah wishlist pengguna.",
        "Menjelaskan algoritma pencarian, scoring metadata, rekomendasi populer, dan ringkasan AI secara sistematis.",
        "Menyusun laporan tugas kecerdasan buatan yang lengkap dengan referensi ilmiah minimal 10 sumber.",
    ]),
    ("h2", "1.4 Manfaat"),
    ("list", [
        "Bagi pengguna, BookAI membantu menemukan buku dan memahami isi buku secara lebih cepat.",
        "Bagi mahasiswa, proyek ini menjadi contoh penerapan AI, API eksternal, database, dan framework web dalam satu aplikasi.",
        "Bagi pengembangan berikutnya, project ini dapat diperluas menjadi sistem rekomendasi personal berbasis riwayat pencarian, wishlist, rating, dan profil pengguna.",
    ]),
    ("h2", "1.5 Batasan Sistem"),
    ("list", [
        "AI aktif digunakan untuk membuat ringkasan buku, poin penting, dan target pembaca.",
        "Rekomendasi personal berbasis machine learning belum diterapkan secara penuh.",
        "Buku populer dihitung dari jumlah data wishlist, bukan dari training model rekomendasi.",
        "Data buku berasal dari OpenLibrary API, sehingga kelengkapan metadata tergantung pada data OpenLibrary.",
        "Hasil ringkasan AI bergantung pada kualitas prompt, model LLM, dan judul buku yang dimasukkan pengguna.",
    ]),
    ("page", ""),
    ("h1", "BAB II DASAR TEORI"),
    ("h2", "2.1 Kecerdasan Buatan"),
    ("p", (
        "Kecerdasan buatan adalah bidang ilmu komputer yang membuat sistem mampu melakukan tugas yang biasanya membutuhkan "
        "kecerdasan manusia, seperti memahami bahasa, mengambil keputusan, mengenali pola, dan memberikan rekomendasi. "
        "Pada BookAI, AI digunakan dalam bentuk pemrosesan bahasa alami untuk menghasilkan ringkasan buku. AI tidak "
        "menggantikan seluruh proses sistem, tetapi menjadi komponen yang memberi nilai tambah pada informasi buku."
    )),
    ("h2", "2.2 Natural Language Processing"),
    ("p", (
        "Natural Language Processing atau NLP adalah cabang AI yang berfokus pada pengolahan bahasa manusia. Fitur "
        "ringkasan AI BookAI termasuk tugas NLP karena sistem menerima input berupa judul buku dan menghasilkan teks "
        "ringkasan, daftar poin penting, serta target pembaca. NLP modern banyak memanfaatkan model transformer dan LLM "
        "karena mampu memahami konteks bahasa secara lebih baik dibanding pendekatan berbasis aturan sederhana."
    )),
    ("h2", "2.3 Large Language Model"),
    ("p", (
        "Large Language Model adalah model AI yang dilatih pada korpus teks besar untuk memprediksi dan menghasilkan teks. "
        "LLM dapat digunakan untuk tanya jawab, klasifikasi teks, ringkasan, pembuatan konten, dan ekstraksi informasi. "
        f"Survei tentang keluarga GPT menunjukkan bahwa model bahasa besar menjadi fondasi penting untuk banyak aplikasi NLP "
        f"modern ({c('10.1016/j.nlp.2023.100048')}). Pada BookAI, LLM diakses melalui Groq API dengan model "
        "llama-3.3-70b-versatile."
    )),
    ("h2", "2.4 Automatic Text Summarization"),
    ("p", (
        "Automatic text summarization adalah teknik menghasilkan versi singkat dari suatu informasi. Terdapat dua pendekatan "
        "umum, yaitu extractive summarization dan abstractive summarization. Extractive summarization memilih kalimat penting "
        "dari teks asli, sedangkan abstractive summarization membuat kalimat baru yang merangkum makna utama. Fitur BookAI "
        "lebih dekat dengan abstractive summarization karena AI menghasilkan ringkasan baru berdasarkan pengetahuan model "
        f"dan instruksi prompt. Penelitian summarization berbasis transformer mendukung kemampuan model untuk menyusun "
        f"ringkasan yang lebih natural ({c('10.1016/j.aej.2023.01.008')}; {c('10.33795/jip.v10i4.5242')})."
    )),
    ("h2", "2.5 Sistem Rekomendasi"),
    ("p", (
        "Sistem rekomendasi adalah sistem yang membantu pengguna memilih item yang relevan. Pendekatan umum dalam sistem "
        "rekomendasi meliputi content-based filtering, collaborative filtering, hybrid filtering, dan pendekatan deep learning. "
        f"Hybrid recommender berbasis BERT menunjukkan bahwa content-based dan collaborative filtering dapat digabungkan untuk "
        f"memperbaiki kualitas rekomendasi ({c('10.1109/access.2022.3177610')}). Pada project BookAI saat ini, sistem belum "
        "melatih model rekomendasi personal, tetapi sudah memiliki fitur rekomendasi populer berdasarkan data wishlist."
    )),
    ("h2", "2.6 API dan Integrasi Data Buku"),
    ("p", (
        "API adalah mekanisme yang memungkinkan aplikasi bertukar data dengan layanan lain. BookAI menggunakan OpenLibrary API "
        "untuk mengambil data buku seperti judul, penulis, tahun terbit, bahasa, dan cover. Backend Django juga menyediakan "
        "endpoint internal seperti /api/search/, /api/book-detail/, /api/popular/, dan /api/favorite/toggle/. Implementasi "
        f"REST API membantu aplikasi mengirim dan menerima data secara terstruktur ({c('10.25181/rt.v1i1.2700')})."
    )),
    ("h2", "2.7 Django dan Database"),
    ("p", (
        "Django adalah framework web berbasis Python yang memakai pola Model-Template-View. Pada BookAI, model digunakan untuk "
        "menyimpan Wishlist, SearchHistory, LoginHistory, Contact, EmailOTP, AIRecommendation, dan SavedSummary. Database aktif "
        "pada konfigurasi project mengarah ke MySQL dengan nama database db_buku. Penyimpanan database diperlukan agar sistem "
        "dapat menyimpan user, buku favorit, hasil AI, histori pencarian, histori login, dan feedback."
    )),
    ("h2", "2.8 Pengujian Black Box"),
    ("p", (
        "Black box testing adalah pengujian yang berfokus pada input dan output tanpa melihat detail kode program. Pengujian "
        "ini cocok untuk memastikan fitur user berjalan sesuai kebutuhan, misalnya login, pencarian buku, tambah favorit, "
        f"dan ringkasan AI ({c('10.33084/jsakti.v3i2.1932')})."
    )),
    ("h2", "2.9 Tinjauan Penelitian Terdahulu"),
    ("table", {
        "headers": ["No", "Topik", "Referensi", "Relevansi dengan BookAI"],
        "rows": [
            ["1", "Deep recommender system", c("10.1016/j.knosys.2023.110335"), "Dasar pengembangan sistem rekomendasi modern."],
            ["2", "Intent-aware recommender", c("10.1145/3700890"), "Menjelaskan rekomendasi berdasarkan niat/kebutuhan user."],
            ["3", "LLM untuk recommender", c("10.1109/access.2024.3368027"), "Menjadi arah pengembangan personalisasi BookAI berikutnya."],
            ["4", "Hybrid recommender", c("10.1109/access.2022.3177610"), "Dasar teori gabungan content-based dan collaborative filtering."],
            ["5", "Content-based filtering", c("10.12962/j24068535.v22i1.a1193"), "Relevan untuk rekomendasi berdasarkan metadata buku."],
            ["6", "Book recommendation", c("10.31586/ijmebac.2022.341"), "Relevan langsung dengan domain rekomendasi buku."],
            ["7", "Item-based collaborative filtering", c("10.1149/10701.15439ecst"), "Relevan untuk pengembangan rekomendasi dari wishlist/rating."],
            ["8", "Large language model", c("10.1016/j.nlp.2023.100048"), "Dasar penggunaan LLM untuk fitur ringkasan."],
            ["9", "LLM dalam riset survei", c("10.1016/j.nlp.2023.100020"), "Menunjukkan kemampuan LLM dalam pemrosesan bahasa."],
            ["10", "Abstractive summarization", c("10.1016/j.aej.2023.01.008"), "Dasar fitur ringkasan AI."],
            ["11", "Indonesian summarization", c("10.33795/jip.v10i4.5242"), "Relevan karena ringkasan BookAI memakai Bahasa Indonesia."],
            ["12", "REST API", c("10.25181/rt.v1i1.2700"), "Dasar integrasi endpoint dan layanan eksternal."],
        ],
    }),
    ("page", ""),
    ("h1", "BAB III ANALISIS DAN PERANCANGAN"),
    ("h2", "3.1 Gambaran Umum Sistem"),
    ("p", (
        "BookAI adalah aplikasi web berbasis Django yang memiliki dua kemampuan utama. Pertama, aplikasi menyediakan pencarian "
        "dan penyimpanan buku berdasarkan data OpenLibrary. Kedua, aplikasi menyediakan ringkasan AI untuk membantu pengguna "
        "memahami gambaran isi buku. Sistem juga memiliki autentikasi, halaman favorit, buku populer, feedback user, dan pesan admin."
    )),
    ("h2", "3.2 Kebutuhan Fungsional"),
    ("list", [
        "User dapat melakukan register, login, dan logout.",
        "User dapat mencari buku berdasarkan judul melalui OpenLibrary API.",
        "User dapat membuka detail buku melalui modal.",
        "User login dapat menambah dan menghapus buku dari favorit.",
        "Sistem dapat menampilkan buku populer berdasarkan jumlah wishlist.",
        "User login dapat membuat ringkasan buku menggunakan AI.",
        "Hasil ringkasan AI disimpan ke Wishlist agar dapat dilihat kembali.",
        "User dapat mengirim feedback, sedangkan admin dapat membalas dan menghapus pesan.",
    ]),
    ("h2", "3.3 Kebutuhan Non Fungsional"),
    ("list", [
        "Usability: tampilan dibuat sederhana dengan navigasi Home, Ringkasan AI, Favorites, About, Feedback, dan Pesan.",
        "Security: fitur penting dibatasi dengan login_required dan request POST menggunakan CSRF token.",
        "Reliability: OpenLibrary request memiliki helper metadata dan fallback ketika data tidak lengkap.",
        "Maintainability: project dipisah ke models.py, views.py, urls.py, templates, static CSS, dan static JS.",
        "Scalability: fitur rekomendasi personal dapat dikembangkan dari data SearchHistory dan Wishlist.",
    ]),
    ("h2", "3.4 Arsitektur Sistem"),
    ("p", "Alur arsitektur BookAI dapat dijelaskan sebagai berikut:"),
    ("code", (
        "User Browser\n"
        "-> Django URL Routing\n"
        "-> View pada main/views.py\n"
        "-> Database MySQL untuk user, wishlist, history, dan feedback\n"
        "-> OpenLibrary API untuk metadata buku\n"
        "-> Groq API untuk ringkasan AI\n"
        "-> Template HTML dan JavaScript menampilkan hasil ke user"
    )),
    ("h2", "3.5 Perancangan Data"),
    ("table", {
        "headers": ["Model", "Fungsi"],
        "rows": [
            ["Wishlist", "Menyimpan buku favorit dan hasil ringkasan AI user."],
            ["SearchHistory", "Menyimpan riwayat pencarian user."],
            ["LoginHistory", "Menyimpan riwayat login user."],
            ["Contact", "Menyimpan feedback user dan balasan admin."],
            ["EmailOTP", "Menyimpan kode OTP, tetapi belum menjadi alur utama register."],
            ["AIRecommendation", "Disiapkan untuk data AI, tetapi belum digunakan oleh view aktif."],
            ["SavedSummary", "Disiapkan untuk ringkasan terpisah, tetapi implementasi aktif menyimpan ringkasan ke Wishlist."],
        ],
    }),
    ("page", ""),
    ("h1", "BAB IV ALGORITMA DAN IMPLEMENTASI AI"),
    ("h2", "4.1 Algoritma Pencarian Buku"),
    ("p", (
        "Pencarian buku dijalankan pada endpoint /api/search/. User memasukkan query, kemudian backend mengirim request ke "
        "OpenLibrary Search API memakai parameter title. Hasil API diubah menjadi format JSON yang lebih sederhana berisi key, "
        "title, author, year, cover_url, language, description, dan is_favorite. Jika user login, query juga disimpan ke SearchHistory."
    )),
    ("code", (
        "Algoritma Pencarian Buku:\n"
        "1. Ambil parameter q dari request.\n"
        "2. Jika q kosong, kembalikan books kosong.\n"
        "3. Jika user login, simpan q ke SearchHistory.\n"
        "4. Kirim request ke https://openlibrary.org/search.json?title=q.\n"
        "5. Untuk setiap buku, ambil key, title, author, year, cover_i, dan language.\n"
        "6. Bentuk cover_url dari cover_i.\n"
        "7. Cek apakah buku sudah ada di Wishlist user.\n"
        "8. Kirim daftar buku sebagai JSON ke frontend."
    )),
    ("h2", "4.2 Algoritma Scoring Metadata Buku"),
    ("p", (
        "Ketika detail buku dibuka atau ringkasan AI dibuat, sistem memakai helper _fetch_openlibrary_meta(). Karena hasil "
        "OpenLibrary dapat lebih dari satu, sistem memilih dokumen terbaik dengan fungsi _score_openlibrary_doc(). Skor diberikan "
        "berdasarkan kecocokan book_key, kecocokan judul, ketersediaan tahun terbit, bahasa, cover, dan author."
    )),
    ("table", {
        "headers": ["Kriteria", "Bobot"],
        "rows": [
            ["book_key sama dengan data yang dicari", "+50"],
            ["judul sama persis", "+30"],
            ["judul mengandung query", "+12"],
            ["memiliki first_publish_year", "+8"],
            ["memiliki language", "+8"],
            ["memiliki cover_i", "+4"],
            ["memiliki author_name", "+4"],
        ],
    }),
    ("code", (
        "Algoritma Scoring Metadata:\n"
        "1. Ambil maksimal 5 hasil dari OpenLibrary.\n"
        "2. Hitung skor setiap dokumen.\n"
        "3. Pilih dokumen dengan skor tertinggi.\n"
        "4. Ubah dokumen menjadi metadata standar: title, author, year, language, cover_url, description.\n"
        "5. Gunakan metadata untuk modal detail, favorites, popular books, atau halaman ringkasan AI."
    )),
    ("h2", "4.3 Algoritma Rekomendasi Populer"),
    ("p", (
        "Fitur buku populer pada BookAI bukan model machine learning, tetapi algoritma agregasi berbasis perilaku user. Sistem "
        "menghitung jumlah Wishlist untuk setiap book_key, lalu mengurutkan buku dari jumlah wishlist terbanyak. Pendekatan ini "
        "dapat disebut popularity-based recommendation karena item yang paling banyak dipilih user dianggap lebih menarik untuk "
        "ditampilkan kepada user lain."
    )),
    ("code", (
        "Algoritma Buku Populer:\n"
        "1. Ambil semua data Wishlist.\n"
        "2. Kelompokkan berdasarkan book_key, title, author, dan cover_id.\n"
        "3. Hitung jumlah wishlist_count untuk setiap buku.\n"
        "4. Urutkan dari wishlist_count terbesar.\n"
        "5. Ambil sesuai limit, misalnya 6 di Home atau 50 di halaman popular-books.\n"
        "6. Tambahkan metadata OpenLibrary jika parameter detail=1.\n"
        "7. Kirim hasil ke frontend."
    )),
    ("h2", "4.4 Algoritma Ringkasan AI"),
    ("p", (
        "Bagian AI paling utama pada BookAI berada di view ringkasan_ai. User memasukkan judul buku, lalu sistem mencari "
        "metadata buku dari OpenLibrary. Setelah itu backend membuat prompt dalam Bahasa Indonesia dan mengirimnya ke Groq API "
        "menggunakan model llama-3.3-70b-versatile. Model diminta mengembalikan JSON valid tanpa markdown agar hasil mudah "
        "diproses oleh program."
    )),
    ("p", (
        "Output AI yang diminta terdiri dari tiga komponen: ringkasan minimal 150 kata, empat poin penting, dan daftar target "
        "pembaca yang cocok. Setelah response diterima, sistem membersihkan tanda markdown seperti ```json dan ```, lalu melakukan "
        "json.loads(). Jika parsing berhasil, hasil disimpan ke model Wishlist menggunakan update_or_create dengan book_key "
        "berformat ai-{judul buku}. Penyimpanan ini membuat hasil AI muncul kembali pada halaman Favorites."
    )),
    ("code", (
        "Algoritma Ringkasan AI BookAI:\n"
        "1. User login membuka /ringkasan-ai/.\n"
        "2. User mengisi judul buku.\n"
        "3. Sistem mengambil metadata buku dari OpenLibrary.\n"
        "4. Sistem membuat prompt:\n"
        "   - ringkasan minimal 150 kata\n"
        "   - poin_penting berisi 4 poin\n"
        "   - cocok_untuk berisi target pembaca\n"
        "   - output harus JSON valid tanpa markdown\n"
        "5. Sistem memanggil Groq chat completion dengan model llama-3.3-70b-versatile.\n"
        "6. Sistem mengambil response.choices[0].message.content.\n"
        "7. Sistem menghapus pembungkus markdown jika ada.\n"
        "8. Sistem parsing JSON.\n"
        "9. Sistem mengambil ringkasan, poin_penting, dan cocok_untuk.\n"
        "10. Sistem menyimpan hasil ke Wishlist.\n"
        "11. Template menampilkan cover, judul, ringkasan, poin penting, dan target pembaca."
    )),
    ("h2", "4.5 Prompt AI yang Digunakan"),
    ("code", (
        "Buat ringkasan buku \"{book_title}\" dalam Bahasa Indonesia.\n\n"
        "Berikan output JSON VALID tanpa markdown.\n\n"
        "Format:\n"
        "{\n"
        "  \"ringkasan\": \"ringkasan minimal 150 kata\",\n"
        "  \"poin_penting\": [\"poin 1\", \"poin 2\", \"poin 3\", \"poin 4\"],\n"
        "  \"cocok_untuk\": [\"Mahasiswa\", \"Karyawan\", \"Pengusaha\"]\n"
        "}"
    )),
    ("h2", "4.6 Kelebihan dan Keterbatasan AI"),
    ("table", {
        "headers": ["Aspek", "Penjelasan"],
        "rows": [
            ["Kelebihan", "Ringkasan dapat dibuat cepat, berbahasa Indonesia, dan tersimpan otomatis ke Wishlist."],
            ["Kelebihan", "Output JSON membuat hasil AI mudah dipisah menjadi ringkasan, poin penting, dan target pembaca."],
            ["Keterbatasan", "AI dapat menghasilkan ringkasan yang kurang akurat jika judul ambigu atau data buku tidak jelas."],
            ["Keterbatasan", "Belum ada verifikasi isi ringkasan terhadap teks buku asli."],
            ["Keterbatasan", "Belum ada model rekomendasi personal yang dilatih dari histori user."],
            ["Pengembangan", "Data Wishlist dan SearchHistory dapat dipakai untuk collaborative filtering atau content-based recommendation."],
        ],
    }),
    ("page", ""),
    ("h1", "BAB V HASIL APLIKASI"),
    ("h2", "5.1 Teknologi yang Digunakan"),
    ("table", {
        "headers": ["Komponen", "Teknologi"],
        "rows": [
            ["Backend", "Python dan Django 4.2.23"],
            ["Frontend", "HTML, CSS, JavaScript, Django Template"],
            ["Database", "MySQL db_buku sesuai konfigurasi settings.py"],
            ["API Buku", "OpenLibrary Search API dan Covers API"],
            ["AI", "Groq API dengan model llama-3.3-70b-versatile"],
            ["Autentikasi", "Django Authentication dan django-allauth untuk opsi Google login"],
            ["Pengujian", "Django TestCase dan skenario black box"],
        ],
    }),
    ("h2", "5.2 Fitur Aplikasi"),
    ("list", [
        "Halaman Home sebagai dashboard utama dengan search bar dan buku populer.",
        "Pencarian buku berdasarkan judul dari OpenLibrary API.",
        "Modal detail buku berisi cover, judul, author, tahun, bahasa, deskripsi, dan tombol favorit.",
        "Wishlist/Favorites untuk menyimpan buku dan hasil ringkasan AI.",
        "Buku populer berdasarkan jumlah data Wishlist.",
        "Ringkasan AI berisi ringkasan, poin penting, dan target pembaca.",
        "Register, login, logout, dan riwayat login.",
        "Feedback user dan pesan admin.",
        "Riwayat pencarian pada SearchHistory.",
    ]),
    ("h2", "5.3 Hasil Implementasi Berdasarkan File Project"),
    ("table", {
        "headers": ["File", "Peran dalam Aplikasi"],
        "rows": [
            ["main/views.py", "Logika pencarian, detail buku, favorite, popular books, ringkasan AI, feedback, pesan, login, register, dan logout."],
            ["main/models.py", "Struktur database Wishlist, SearchHistory, LoginHistory, Contact, EmailOTP, AIRecommendation, dan SavedSummary."],
            ["main/urls.py", "Routing halaman dan endpoint API."],
            ["main/static/js/app.js", "Modal buku, fetch API, toggle favorite, render card buku, dan input OTP."],
            ["main/static/css/style.css", "Desain tampilan BookAI."],
            ["main/templates/ringkasan_ai.html", "Tampilan form dan hasil ringkasan AI."],
            ["main/templates/favorites.html", "Tampilan buku favorit dan hasil AI tersimpan."],
            ["main/tests.py", "Test autentikasi dan visibilitas feedback."],
        ],
    }),
    ("h2", "5.4 Skenario Penggunaan"),
    ("list", [
        "User melakukan register dan login.",
        "User mencari buku dari halaman Home.",
        "User membuka modal detail buku.",
        "User menyimpan buku ke Favorites.",
        "User membuka halaman Ringkasan AI dan memasukkan judul buku.",
        "Sistem membuat ringkasan dengan Groq AI.",
        "Hasil ringkasan disimpan ke Wishlist dan dapat dilihat di Favorites.",
        "User mengirim feedback, kemudian admin dapat membalas melalui halaman Pesan.",
    ]),
    ("h2", "5.5 Pengujian Black Box"),
    ("table", {
        "headers": ["No", "Skenario", "Input", "Output yang Diharapkan", "Hasil"],
        "rows": [
            ["1", "Register berhasil", "Username, email, password valid", "Akun dibuat dan diarahkan ke login", "Berhasil"],
            ["2", "Register gagal", "Username sudah dipakai", "Pesan username sudah digunakan tampil", "Berhasil"],
            ["3", "Login berhasil", "Username dan password benar", "User masuk ke Home dan LoginHistory tersimpan", "Berhasil"],
            ["4", "Login gagal", "Username/password salah", "Pesan error tampil", "Berhasil"],
            ["5", "Pencarian buku", "Judul buku", "Daftar buku dari OpenLibrary tampil", "Berhasil"],
            ["6", "Detail buku", "Klik card buku", "Modal detail tampil", "Berhasil"],
            ["7", "Tambah favorit", "Klik Tambah ke Favorit", "Buku tersimpan di Wishlist", "Berhasil"],
            ["8", "Hapus favorit", "Klik Hapus dari Favorit", "Buku dihapus dari Wishlist", "Berhasil"],
            ["9", "Ringkasan AI", "Judul buku", "Ringkasan, poin penting, dan target pembaca tampil", "Berhasil jika API key aktif"],
            ["10", "Kirim feedback", "Nama dan pesan valid", "Feedback tersimpan di Contact", "Berhasil"],
            ["11", "Admin membalas pesan", "Isi balasan admin", "Balasan tersimpan", "Berhasil"],
            ["12", "Admin menghapus pesan", "Klik hapus", "Pesan terhapus", "Berhasil"],
        ],
    }),
    ("h2", "5.6 Catatan Evaluasi"),
    ("p", (
        "Berdasarkan kode project, beberapa fitur sudah berjalan sebagai fitur aktif, yaitu pencarian buku, detail buku, "
        "wishlist, buku populer, ringkasan AI, feedback, pesan admin, login, register, riwayat login, dan riwayat pencarian. "
        "Namun ada beberapa fitur yang masih bersifat potensial, yaitu EmailOTP, SavedSummary, AIRecommendation, dan reset password. "
        "Selain itu, beberapa teks lama pada dokumentasi/tampilan perlu disamakan agar konsisten menyebut Groq AI, bukan Gemini atau DeepSeek, "
        "karena view aktif untuk ringkasan menggunakan Groq."
    )),
    ("page", ""),
    ("h1", "BAB VI PENUTUP"),
    ("h2", "6.1 Kesimpulan"),
    ("list", [
        "BookAI berhasil dirancang sebagai aplikasi berbasis kecerdasan buatan yang membantu pengguna mencari buku dan membuat ringkasan buku.",
        "Integrasi OpenLibrary API memungkinkan aplikasi mengambil metadata buku tanpa memasukkan data secara manual.",
        "Integrasi Groq API dengan model llama-3.3-70b-versatile memungkinkan sistem membuat ringkasan, poin penting, dan target pembaca dalam Bahasa Indonesia.",
        "Algoritma AI pada BookAI terdiri dari pengambilan judul, pencarian metadata, penyusunan prompt, pemanggilan LLM, pembersihan output, parsing JSON, penyimpanan ke Wishlist, dan penampilan hasil.",
        "Fitur rekomendasi populer dihitung berdasarkan jumlah wishlist, sehingga masih bersifat popularity-based recommendation dan belum menjadi rekomendasi personal penuh.",
    ]),
    ("h2", "6.2 Saran Pengembangan"),
    ("list", [
        "Menambahkan rekomendasi personal berbasis SearchHistory, Wishlist, rating, dan genre buku.",
        "Mengembangkan content-based filtering menggunakan judul, author, subject, dan deskripsi buku.",
        "Mengembangkan collaborative filtering berdasarkan kesamaan wishlist antar user.",
        "Menambahkan validasi ringkasan AI dengan sumber metadata atau sinopsis resmi jika tersedia.",
        "Menyimpan hasil AI ke model khusus SavedSummary agar data ringkasan lebih terpisah dari wishlist biasa.",
        "Mengaktifkan OTP email dan reset password secara penuh.",
        "Merapikan label AI agar konsisten dengan implementasi Groq.",
        "Menambahkan evaluasi UAT dan pengukuran response time untuk fitur pencarian serta ringkasan AI.",
        "Memastikan seluruh credential rahasia disimpan di environment variable dan tidak ditulis langsung di source code.",
    ]),
    ("page", ""),
    ("h1", "DAFTAR PUSTAKA"),
]

for idx, item in enumerate(refs, start=1):
    sections.append(("p", f"[{idx}] {ref_apa(item)}"))


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(col).replace("|", "\\|") for col in row) + " |")
    return "\n".join(lines)


def write_markdown():
    lines = []
    for kind, value in sections:
        if kind == "title":
            lines.append(f"# {value}")
        elif kind == "center":
            lines.append(value)
        elif kind == "h1":
            lines.append(f"\n# {value}")
        elif kind == "h2":
            lines.append(f"\n## {value}")
        elif kind == "p":
            lines.append(f"\n{value}")
        elif kind == "list":
            lines.append("")
            lines.extend(f"- {item}" for item in value)
        elif kind == "code":
            lines.append("\n```text")
            lines.append(value)
            lines.append("```")
        elif kind == "table":
            lines.append("")
            lines.append(markdown_table(value["headers"], value["rows"]))
        elif kind == "page":
            lines.append("\n---")
    MD_OUT.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def xml_text(text):
    return escape(str(text), quote=False)


def paragraph(text="", style=None, align=None, bold=False, italic=False):
    props = []
    if style:
        props.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        props.append(f'<w:jc w:val="{align}"/>')
    ppr = f"<w:pPr>{''.join(props)}</w:pPr>" if props else ""
    rpr_parts = []
    if bold:
        rpr_parts.append("<w:b/>")
    if italic:
        rpr_parts.append("<w:i/>")
    rpr = f"<w:rPr>{''.join(rpr_parts)}</w:rPr>" if rpr_parts else ""
    return f"<w:p>{ppr}<w:r>{rpr}<w:t>{xml_text(text)}</w:t></w:r></w:p>"


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def table_xml(headers, rows):
    width = max(1200, int(9000 / max(1, len(headers))))

    def cell(text, header=False):
        shading = '<w:shd w:fill="EDE4FF"/>' if header else ""
        bold = "<w:b/>" if header else ""
        return (
            "<w:tc>"
            "<w:tcPr>"
            f'<w:tcW w:w="{width}" w:type="dxa"/>'
            f"{shading}"
            "</w:tcPr>"
            f"<w:p><w:r><w:rPr>{bold}</w:rPr><w:t>{xml_text(text)}</w:t></w:r></w:p>"
            "</w:tc>"
        )

    border = (
        "<w:tblPr>"
        "<w:tblBorders>"
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="B7A9E8"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="B7A9E8"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="B7A9E8"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="B7A9E8"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="B7A9E8"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="B7A9E8"/>'
        "</w:tblBorders>"
        "</w:tblPr>"
    )
    xml = [f"<w:tbl>{border}"]
    xml.append("<w:tr>" + "".join(cell(h, True) for h in headers) + "</w:tr>")
    for row in rows:
        xml.append("<w:tr>" + "".join(cell(col) for col in row) + "</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


def write_docx():
    body = []
    for kind, value in sections:
        if kind == "title":
            body.append(paragraph(value, style="Title", align="center", bold=True))
        elif kind == "center":
            body.append(paragraph(value, align="center"))
        elif kind == "h1":
            body.append(paragraph(value, style="Heading1", bold=True))
        elif kind == "h2":
            body.append(paragraph(value, style="Heading2", bold=True))
        elif kind == "p":
            body.append(paragraph(value))
        elif kind == "list":
            for item in value:
                body.append(paragraph(f"- {item}"))
        elif kind == "code":
            for line in value.splitlines():
                body.append(paragraph(line, style="Code"))
        elif kind == "table":
            body.append(table_xml(value["headers"], value["rows"]))
        elif kind == "page":
            body.append(page_break())

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {''.join(body)}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>
"""

    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr><w:b/><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr>
    <w:rPr><w:b/><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="28"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:before="200" w:after="100"/></w:pPr>
    <w:rPr><w:b/><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="26"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Code">
    <w:name w:val="Code"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="20"/></w:rPr>
  </w:style>
</w:styles>
"""

    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>
"""

    rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

    doc_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""

    with ZipFile(DOCX_OUT, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types_xml)
        z.writestr("_rels/.rels", rels_xml)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/styles.xml", styles_xml)
        z.writestr("word/_rels/document.xml.rels", doc_rels_xml)


if __name__ == "__main__":
    write_markdown()
    write_docx()
    print(MD_OUT)
    print(DOCX_OUT)
