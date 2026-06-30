from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import json


OUT_DOCX = Path("Laporan_Kecerdasan_Buatan_BookAI.docx")
OUT_MD = Path("Laporan_Kecerdasan_Buatan_BookAI.md")
REF_PATH = Path("references_crossref_raw.json")


def xml_text(text):
    return escape(str(text), quote=False)


def paragraph(text="", style=None, align=None, bold=False, italic=False):
    props = []
    if style:
        props.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        props.append(f'<w:jc w:val="{align}"/>')
    ppr = f"<w:pPr>{''.join(props)}</w:pPr>" if props else ""

    r_props = []
    if bold:
        r_props.append("<w:b/>")
    if italic:
        r_props.append("<w:i/>")
    rpr = f"<w:rPr>{''.join(r_props)}</w:rPr>" if r_props else ""

    return f"<w:p>{ppr}<w:r>{rpr}<w:t>{xml_text(text)}</w:t></w:r></w:p>"


def heading(text, level=1):
    return paragraph(text, style=f"Heading{level}")


def bullet(text):
    return paragraph(f"- {text}")


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def table(headers, rows):
    def cell(text, header=False):
        fill = '<w:shd w:fill="EDE4FF"/>' if header else ""
        bold = "<w:b/>" if header else ""
        return (
            "<w:tc>"
            "<w:tcPr>"
            '<w:tcW w:w="2600" w:type="dxa"/>'
            f"{fill}"
            "</w:tcPr>"
            f"<w:p><w:r><w:rPr>{bold}</w:rPr><w:t>{xml_text(text)}</w:t></w:r></w:p>"
            "</w:tc>"
        )

    borders = (
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
    xml = [f"<w:tbl>{borders}"]
    xml.append("<w:tr>" + "".join(cell(h, True) for h in headers) + "</w:tr>")
    for row in rows:
        xml.append("<w:tr>" + "".join(cell(col) for col in row) + "</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


def load_refs():
    if not REF_PATH.exists():
        return []
    return json.loads(REF_PATH.read_text(encoding="utf-8"))


def ref_title(item):
    return (item.get("title") or [""])[0].strip()


def ref_journal(item):
    return (item.get("container-title") or [""])[0].strip()


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


def ref_apa(item):
    authors = ref_authors(item)
    if not authors:
        authors_text = "Tanpa penulis"
    elif len(authors) == 1:
        authors_text = authors[0]
    else:
        authors_text = ", ".join(authors[:-1]) + ", & " + authors[-1]

    doi = item.get("DOI", "").lower()
    url = f"https://doi.org/{doi}" if doi else item.get("URL", "")
    return f"{authors_text}. ({ref_year(item)}). {ref_title(item)}. {ref_journal(item)}. {url}"


refs = load_refs()[:12]


body = []
md = []


def add_title(text):
    body.append(paragraph(text, style="Title", align="center", bold=True))
    md.append(f"# {text}\n")


def add_heading(text, level=1):
    body.append(heading(text, level))
    md.append(f"{'#' * min(level + 1, 6)} {text}\n")


def add_para(text):
    body.append(paragraph(text))
    md.append(f"{text}\n")


def add_bullet(text):
    body.append(bullet(text))
    md.append(f"- {text}\n")


def add_table(headers, rows):
    body.append(table(headers, rows))
    md.append("| " + " | ".join(headers) + " |")
    md.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        md.append("| " + " | ".join(str(col).replace("\n", " ") for col in row) + " |")
    md.append("")


add_title("LAPORAN TUGAS KECERDASAN BUATAN")
body.append(paragraph("Aplikasi BookAI: Website Rekomendasi dan Ringkasan Buku Berbasis AI", align="center", bold=True))
md.append("**Aplikasi BookAI: Website Rekomendasi dan Ringkasan Buku Berbasis AI**\n")
body.append(paragraph(""))
body.append(paragraph("Disusun oleh:", align="center"))
body.append(paragraph("Nama Mahasiswa : [Isi Nama Mahasiswa]", align="center"))
body.append(paragraph("NIM : [Isi NIM]", align="center"))
body.append(paragraph("Kelas : [Isi Kelas]", align="center"))
body.append(paragraph("Mata Kuliah : Kecerdasan Buatan", align="center"))
body.append(paragraph("Dosen Pengampu : [Isi Nama Dosen]", align="center"))
body.append(paragraph("Program Studi : [Isi Program Studi]", align="center"))
body.append(paragraph("Tahun Akademik : [Isi Tahun Akademik]", align="center"))
md.extend([
    "Nama Mahasiswa : [Isi Nama Mahasiswa]",
    "NIM : [Isi NIM]",
    "Kelas : [Isi Kelas]",
    "Mata Kuliah : Kecerdasan Buatan",
    "Dosen Pengampu : [Isi Nama Dosen]",
    "Program Studi : [Isi Program Studi]",
    "Tahun Akademik : [Isi Tahun Akademik]\n",
])
body.append(page_break())

add_heading("ABSTRAK", 1)
add_para(
    "BookAI adalah aplikasi berbasis web yang menerapkan konsep kecerdasan buatan untuk membantu pengguna mencari, memilih, dan memahami isi buku secara lebih cepat. "
    "Aplikasi ini dikembangkan menggunakan Django, HTML, CSS, JavaScript, MySQL, OpenLibrary API, dan Groq AI dengan model llama-3.3-70b-versatile. "
    "Permasalahan yang diangkat adalah banyaknya pilihan buku yang membuat pengguna kesulitan menentukan bacaan yang sesuai, serta keterbatasan waktu pengguna untuk membaca deskripsi panjang sebelum memilih buku. "
    "Dalam sistem ini, AI diterapkan pada dua bagian utama, yaitu rekomendasi buku populer berbasis sinyal wishlist pengguna dan pembuatan ringkasan buku berbasis Natural Language Processing menggunakan Large Language Model. "
    "Pengguna dapat mencari buku dari OpenLibrary, melihat detail buku, menyimpan buku sebagai favorit, melihat daftar buku populer, dan meminta sistem membuat ringkasan buku dalam Bahasa Indonesia. "
    "Hasil implementasi menunjukkan bahwa BookAI dapat menjadi contoh aplikasi kecerdasan buatan yang praktis karena menggabungkan sistem rekomendasi, pemrosesan bahasa alami, integrasi API eksternal, dan penyimpanan data pengguna dalam satu aplikasi."
)
body.append(paragraph("Kata kunci: Kecerdasan Buatan, BookAI, Sistem Rekomendasi, Large Language Model, Ringkasan Buku", bold=True))
md.append("**Kata kunci:** Kecerdasan Buatan, BookAI, Sistem Rekomendasi, Large Language Model, Ringkasan Buku\n")
body.append(page_break())

add_heading("BAB I PENDAHULUAN", 1)
add_heading("1.1 Latar Belakang", 2)
add_para(
    "Perkembangan teknologi informasi membuat akses terhadap buku semakin mudah. Pengguna dapat mencari buku melalui website, katalog digital, dan perpustakaan daring. "
    "Akan tetapi, jumlah pilihan buku yang sangat banyak sering menimbulkan masalah baru, yaitu pengguna membutuhkan waktu lama untuk menemukan buku yang benar-benar sesuai dengan minat dan kebutuhannya. "
    "Kondisi ini memperlihatkan pentingnya sistem yang dapat membantu proses pemilihan buku secara lebih cerdas."
)
add_para(
    "Kecerdasan buatan dapat digunakan untuk menyelesaikan masalah tersebut melalui sistem rekomendasi dan pemrosesan bahasa alami. Sistem rekomendasi membantu menyusun pilihan buku berdasarkan sinyal tertentu, misalnya popularitas atau riwayat ketertarikan pengguna. "
    "Sementara itu, Natural Language Processing dan Large Language Model dapat membantu membuat ringkasan buku sehingga pengguna memperoleh gambaran isi buku tanpa harus membaca uraian panjang terlebih dahulu."
)
add_para(
    "Project yang digunakan pada laporan ini adalah website rekomendasi buku bernama BookAI. Berdasarkan struktur project, BookAI dibangun dengan Django sebagai backend, JavaScript sebagai pengatur interaksi frontend, MySQL sebagai database, OpenLibrary API sebagai sumber data buku, dan Groq AI sebagai layanan pembuatan ringkasan. "
    "Karena itu, laporan ini tidak hanya menjelaskan website secara umum, tetapi menitikberatkan pada penerapan kecerdasan buatan yang benar-benar ada pada project, terutama algoritma rekomendasi buku populer dan algoritma ringkasan AI."
)

add_heading("1.2 Rumusan Masalah", 2)
for item in [
    "Bagaimana merancang aplikasi berbasis kecerdasan buatan untuk membantu pengguna menemukan buku?",
    "Bagaimana BookAI memanfaatkan data OpenLibrary dan data wishlist untuk menampilkan buku yang relevan dan populer?",
    "Bagaimana algoritma AI pada BookAI membuat ringkasan buku, poin penting, dan target pembaca?",
    "Bagaimana hasil implementasi aplikasi BookAI berdasarkan fitur yang tersedia pada project?",
]:
    add_bullet(item)

add_heading("1.3 Tujuan", 2)
for item in [
    "Membuat laporan aplikasi berbasis kecerdasan buatan sesuai project BookAI.",
    "Menjelaskan dasar teori kecerdasan buatan, sistem rekomendasi, dan NLP yang digunakan pada aplikasi.",
    "Menjelaskan algoritma rekomendasi buku dan ringkasan AI secara runtut.",
    "Mendeskripsikan hasil aplikasi berupa fitur, alur kerja, dan manfaat bagi pengguna.",
]:
    add_bullet(item)

add_heading("1.4 Manfaat", 2)
for item in [
    "Bagi pengguna, BookAI membantu menemukan buku dan memahami isi buku secara lebih cepat.",
    "Bagi pengembang, project ini menjadi contoh integrasi Django, database, API eksternal, dan model AI.",
    "Bagi pembelajaran kecerdasan buatan, project ini menunjukkan penerapan AI pada kasus nyata, bukan hanya konsep teori.",
]:
    add_bullet(item)

add_heading("1.5 Batasan Masalah", 2)
for item in [
    "Data buku diambil dari OpenLibrary API, bukan dari dataset buku lokal yang dilatih sendiri.",
    "Rekomendasi populer dihitung dari jumlah buku yang masuk wishlist pengguna.",
    "Ringkasan AI dibuat menggunakan Groq API dengan model llama-3.3-70b-versatile.",
    "Personalisasi rekomendasi mendalam berdasarkan profil pengguna belum diterapkan.",
    "Laporan disusun berdasarkan kondisi project website_rekomendasi_buku fix.",
]:
    add_bullet(item)
body.append(page_break())

add_heading("BAB II DASAR TEORI", 1)
add_heading("2.1 Kecerdasan Buatan", 2)
add_para(
    "Kecerdasan buatan adalah bidang ilmu komputer yang berfokus pada pembuatan sistem yang mampu melakukan tugas yang biasanya membutuhkan kecerdasan manusia, seperti memahami bahasa, mengenali pola, mengambil keputusan, dan memberikan rekomendasi. "
    "Pada aplikasi BookAI, kecerdasan buatan digunakan untuk membantu proses pemilihan buku dan menghasilkan ringkasan otomatis dalam Bahasa Indonesia."
)

add_heading("2.2 Sistem Rekomendasi", 2)
add_para(
    "Sistem rekomendasi adalah sistem yang menyaring dan menyusun item agar pengguna lebih mudah menemukan pilihan yang sesuai. "
    "Dalam konteks buku, sistem rekomendasi dapat memanfaatkan data judul, penulis, kategori, rating, riwayat pencarian, atau interaksi pengguna. "
    "Penelitian tentang recommender systems menunjukkan bahwa pendekatan rekomendasi dapat dibangun dengan content-based filtering, collaborative filtering, hybrid filtering, maupun model modern berbasis representasi bahasa (Chen et al., 2023; Jannach dan Zanker, 2024; Channarong et al., 2022)."
)
add_para(
    "BookAI menerapkan bentuk sederhana dari collaborative signal melalui data wishlist. Buku yang paling banyak disimpan pengguna dianggap memiliki tingkat ketertarikan kolektif lebih tinggi, sehingga ditampilkan sebagai buku populer. "
    "Pendekatan ini tidak serumit collaborative filtering penuh, tetapi sudah mencerminkan ide dasar bahwa perilaku pengguna dapat menjadi sinyal rekomendasi."
)

add_heading("2.3 Natural Language Processing dan Large Language Model", 2)
add_para(
    "Natural Language Processing adalah cabang AI yang berhubungan dengan pemrosesan bahasa manusia. Salah satu perkembangan penting NLP adalah Large Language Model, yaitu model bahasa berukuran besar yang mampu memahami instruksi dan menghasilkan teks. "
    "Kajian tentang GPT dan LLM menunjukkan bahwa model bahasa dapat digunakan untuk banyak tugas, termasuk menjawab pertanyaan, menyusun ringkasan, dan membantu analisis teks (Kalyan, 2024; Jansen et al., 2023)."
)
add_para(
    "Pada BookAI, LLM digunakan untuk membuat ringkasan buku berdasarkan judul yang dimasukkan pengguna. Model diminta menghasilkan output JSON yang terdiri dari ringkasan, poin penting, dan target pembaca. "
    "Output terstruktur seperti ini memudahkan backend Django menyimpan dan menampilkan hasil AI pada halaman web."
)

add_heading("2.4 Automatic Text Summarization", 2)
add_para(
    "Automatic text summarization adalah teknik untuk menghasilkan ringkasan dari teks atau informasi tertentu. Ringkasan dapat bersifat ekstraktif, yaitu mengambil kalimat penting dari teks asli, atau abstraktif, yaitu menyusun ulang informasi menjadi kalimat baru. "
    "Penelitian tentang summarization menunjukkan bahwa model transformer dan deep learning banyak digunakan untuk menghasilkan ringkasan yang lebih alami (Ay et al., 2023; Hartawan et al., 2024; D'Silva dan Sharma, 2022). "
    "BookAI menggunakan pendekatan abstraktif karena ringkasan dibuat oleh LLM berdasarkan pengetahuan model dan konteks judul buku."
)

add_heading("2.5 API dan Integrasi Data Buku", 2)
add_para(
    "API memungkinkan aplikasi mengambil data dari layanan lain melalui internet. Pada BookAI, OpenLibrary API digunakan untuk mencari buku berdasarkan judul, mengambil penulis, tahun terbit, bahasa, deskripsi, dan cover. "
    "Integrasi API membuat sistem tidak perlu menyimpan seluruh katalog buku secara lokal."
)

add_heading("2.6 Django dan Database", 2)
add_para(
    "Django adalah framework web berbasis Python yang menyediakan struktur model, view, template, routing, autentikasi, dan admin panel. "
    "Dalam BookAI, Django digunakan untuk mengatur endpoint pencarian buku, favorit, buku populer, ringkasan AI, login, register, feedback, dan pesan admin. "
    "Database MySQL digunakan untuk menyimpan data pengguna, wishlist, riwayat pencarian, riwayat login, dan pesan feedback."
)
body.append(page_break())

add_heading("BAB III ANALISIS DAN PERANCANGAN SISTEM", 1)
add_heading("3.1 Gambaran Umum BookAI", 2)
add_para(
    "BookAI adalah website rekomendasi dan ringkasan buku. Pengguna dapat mencari buku, membuka detail buku, menyimpan buku ke favorit, melihat buku populer, dan membuat ringkasan buku menggunakan AI. "
    "Aplikasi juga menyediakan fitur register, login, logout, feedback pengguna, pesan admin, dan riwayat aktivitas tertentu."
)

add_heading("3.2 Teknologi yang Digunakan", 2)
add_table(
    ["Komponen", "Teknologi", "Fungsi"],
    [
        ["Backend", "Django 4.2.23", "Mengatur route, view, model, autentikasi, dan response JSON."],
        ["Frontend", "HTML, CSS, JavaScript", "Menampilkan halaman, modal detail buku, pencarian, dan interaksi favorit."],
        ["Database", "MySQL", "Menyimpan user, wishlist, riwayat pencarian, riwayat login, dan feedback."],
        ["Data Buku", "OpenLibrary API", "Mengambil data judul, author, tahun, bahasa, deskripsi, dan cover buku."],
        ["AI", "Groq API llama-3.3-70b-versatile", "Membuat ringkasan buku, poin penting, dan target pembaca."],
        ["Autentikasi", "Django Authentication dan django-allauth", "Mengelola login manual dan opsi Google login."],
    ],
)

add_heading("3.3 Model Data Utama", 2)
add_table(
    ["Model", "Data yang Disimpan", "Peran dalam AI/Aplikasi"],
    [
        ["Wishlist", "user, book_key, title, author, cover_id, ai_summary, ai_points, ai_targets, created_at", "Menyimpan favorit dan hasil ringkasan AI. Juga menjadi sinyal untuk buku populer."],
        ["SearchHistory", "user, query, created_at", "Menyimpan riwayat pencarian pengguna."],
        ["LoginHistory", "user, email, ip_address, logged_in_at", "Menyimpan riwayat login."],
        ["Contact", "user, name, email, message, admin_reply, replied_by, replied_at", "Menyimpan feedback pengguna dan balasan admin."],
        ["EmailOTP", "user, otp, created_at", "Disiapkan untuk verifikasi OTP."],
    ],
)

add_heading("3.4 Arsitektur Sistem", 2)
add_para(
    "Alur utama sistem dimulai dari browser pengguna. JavaScript mengirim request ke endpoint Django. Django memproses request, mengambil data dari database atau API eksternal, lalu mengembalikan halaman HTML atau data JSON. "
    "Untuk data buku, Django memanggil OpenLibrary API. Untuk ringkasan AI, Django mengirim prompt ke Groq API dan menerima hasil dalam format JSON. "
    "Hasil tersebut kemudian disimpan ke tabel Wishlist dan ditampilkan kembali kepada pengguna."
)

add_heading("3.5 Fitur yang Dirancang", 2)
for item in [
    "Pencarian buku berdasarkan judul melalui endpoint /api/search/.",
    "Detail buku melalui endpoint /api/book-detail/.",
    "Tambah dan hapus favorit melalui endpoint /api/favorite/toggle/.",
    "Buku populer melalui endpoint /api/popular/ berdasarkan jumlah wishlist.",
    "Ringkasan AI melalui halaman /ringkasan-ai/.",
    "Register, login, logout, Google login, feedback, pesan pengguna, dan pesan admin.",
]:
    add_bullet(item)
body.append(page_break())

add_heading("BAB IV ALGORITMA KECERDASAN BUATAN", 1)
add_heading("4.1 Algoritma Pencarian dan Pengambilan Metadata Buku", 2)
add_para(
    "Pencarian buku pada BookAI menggunakan OpenLibrary Search API. Pengguna memasukkan kata kunci judul, kemudian backend mengirim request ke OpenLibrary dengan parameter title, page, dan limit. "
    "Data yang diterima diproses menjadi struktur sederhana yang berisi key, title, author, year, cover_url, language, description, dan status is_favorite."
)
add_table(
    ["Langkah", "Proses"],
    [
        ["1", "User mengetik judul buku pada search bar."],
        ["2", "JavaScript mengirim request GET ke /api/search/?q=judul."],
        ["3", "Django menyimpan query ke SearchHistory jika user sudah login."],
        ["4", "Django memanggil https://openlibrary.org/search.json dengan parameter title."],
        ["5", "Response JSON dari OpenLibrary diubah menjadi daftar buku yang siap ditampilkan."],
        ["6", "Sistem mengecek apakah setiap buku sudah ada di Wishlist user."],
        ["7", "Frontend menampilkan hasil dalam bentuk card buku."],
    ],
)

add_heading("4.2 Algoritma Rekomendasi Buku Populer", 2)
add_para(
    "Rekomendasi buku populer pada BookAI menggunakan pendekatan popularity-based recommendation. Sistem menghitung jumlah kemunculan setiap buku pada tabel Wishlist. "
    "Semakin banyak pengguna menyimpan buku tertentu, semakin tinggi posisi buku tersebut pada daftar populer. Algoritma ini sederhana, tetapi sesuai dengan data yang sudah tersedia pada project."
)
add_para("Pseudocode algoritma rekomendasi populer:")
add_para(
    "Input: limit jumlah buku yang ingin ditampilkan. "
    "Ambil data Wishlist, kelompokkan berdasarkan book_key, title, author, dan cover_id, hitung jumlah setiap kelompok, urutkan dari jumlah terbesar, ambil sebanyak limit, lalu tampilkan sebagai buku populer."
)
add_table(
    ["Aspek", "Penjelasan"],
    [
        ["Input", "Data Wishlist dari seluruh pengguna."],
        ["Fitur/Sinyal", "Jumlah user yang menyimpan buku sebagai favorit."],
        ["Skor", "wishlist_count = jumlah baris Wishlist untuk book_key tertentu."],
        ["Output", "Daftar buku populer yang diurutkan dari wishlist_count terbesar."],
        ["Kelebihan", "Mudah diterapkan, cepat, dan memanfaatkan interaksi nyata pengguna."],
        ["Keterbatasan", "Belum personal untuk setiap user dan dapat bias pada buku yang sudah lebih dulu populer."],
    ],
)

add_heading("4.3 Algoritma Ringkasan AI dengan Large Language Model", 2)
add_para(
    "Fitur ringkasan AI adalah bagian paling jelas dari penerapan kecerdasan buatan pada BookAI. User memasukkan judul buku pada halaman Ringkasan AI. "
    "Sistem mengambil metadata buku dari OpenLibrary, lalu membuat prompt untuk Groq AI. Model llama-3.3-70b-versatile diminta menghasilkan JSON valid yang berisi ringkasan minimal 150 kata, empat poin penting, dan target pembaca."
)
add_table(
    ["Langkah", "Proses"],
    [
        ["1", "User membuka halaman /ringkasan-ai/ dan memasukkan judul buku."],
        ["2", "Django membaca input POST dengan nama field judul."],
        ["3", "Django memanggil fungsi _fetch_openlibrary_meta untuk mengambil cover, author, tahun, dan bahasa."],
        ["4", "Django membuat prompt dalam Bahasa Indonesia dengan format output JSON."],
        ["5", "Prompt dikirim ke Groq API menggunakan model llama-3.3-70b-versatile."],
        ["6", "Response dari AI dibersihkan dari tanda markdown seperti ```json jika ada."],
        ["7", "Django melakukan json.loads untuk mengubah teks AI menjadi objek Python."],
        ["8", "Nilai ringkasan, poin_penting, dan cocok_untuk diambil dari JSON."],
        ["9", "Hasil AI disimpan atau diperbarui pada tabel Wishlist dengan book_key ai-judul."],
        ["10", "Template ringkasan_ai.html menampilkan ringkasan, poin penting, target pembaca, dan metadata buku."],
    ],
)
add_para("Struktur output yang diminta kepada AI:")
add_para(
    '{"ringkasan": "ringkasan minimal 150 kata", "poin_penting": ["poin 1", "poin 2", "poin 3", "poin 4"], "cocok_untuk": ["Mahasiswa", "Karyawan", "Pengusaha"]}'
)
add_para(
    "Dari sisi kecerdasan buatan, proses ini termasuk penerapan NLP generatif. Model tidak hanya mengambil teks yang sudah ada, tetapi menghasilkan ringkasan baru berdasarkan instruksi yang diberikan. "
    "Penggunaan format JSON membuat hasil AI lebih mudah diproses oleh sistem, karena setiap bagian output memiliki kunci yang jelas."
)

add_heading("4.4 Analisis AI yang Digunakan", 2)
add_table(
    ["Komponen AI", "Jenis AI", "Implementasi pada BookAI"],
    [
        ["Rekomendasi populer", "Popularity-based recommender system", "Mengurutkan buku berdasarkan jumlah wishlist."],
        ["Ringkasan buku", "Natural Language Processing dan Large Language Model", "Membuat ringkasan, poin penting, dan target pembaca dari judul buku."],
        ["Pemrosesan output", "Structured generation", "AI diarahkan mengeluarkan JSON agar mudah diparsing."],
        ["Personalisasi", "Belum penuh", "Data SearchHistory dan Wishlist sudah ada, tetapi belum digunakan untuk model personalisasi yang lebih kompleks."],
    ],
)
body.append(page_break())

add_heading("BAB V HASIL APLIKASI", 1)
add_heading("5.1 Hasil Implementasi", 2)
add_para(
    "Hasil dari project adalah aplikasi BookAI yang dapat dijalankan sebagai website. Aplikasi menyediakan halaman Home, Ringkasan AI, Favorites, Popular Books, About, Feedback, Messages, Login, Register, dan Verify OTP. "
    "Fitur utama yang berhubungan langsung dengan kecerdasan buatan adalah Ringkasan AI dan Buku Populer."
)
add_table(
    ["Fitur", "Hasil yang Diberikan"],
    [
        ["Home", "Menampilkan hero, search bar, hasil pencarian, dan buku populer."],
        ["Pencarian Buku", "User dapat mencari buku berdasarkan judul melalui OpenLibrary API."],
        ["Detail Buku", "User dapat melihat cover, judul, author, tahun, bahasa, dan deskripsi pada modal."],
        ["Favorites", "User dapat menyimpan dan menghapus buku favorit."],
        ["Popular Books", "Sistem menampilkan buku populer berdasarkan jumlah wishlist."],
        ["Ringkasan AI", "Sistem membuat ringkasan, poin penting, dan target pembaca menggunakan Groq AI."],
        ["Feedback dan Pesan", "User dapat mengirim feedback dan admin dapat membalas atau menghapus pesan."],
        ["Autentikasi", "Register, login, logout, dan opsi login Google tersedia."],
    ],
)

add_heading("5.2 Contoh Alur Penggunaan", 2)
for item in [
    "User membuka halaman Home dan mengetik judul buku.",
    "Sistem menampilkan daftar buku dari OpenLibrary.",
    "User membuka modal detail untuk melihat informasi buku.",
    "User menyimpan buku ke Favorites.",
    "Data wishlist ikut memengaruhi daftar Popular Books.",
    "User membuka halaman Ringkasan AI dan memasukkan judul buku.",
    "AI membuat ringkasan buku dalam Bahasa Indonesia.",
    "Ringkasan tersimpan di Wishlist dan dapat dilihat kembali pada halaman Favorites.",
]:
    add_bullet(item)

add_heading("5.3 Kelebihan Aplikasi", 2)
for item in [
    "Menggabungkan pencarian buku dan ringkasan AI dalam satu aplikasi.",
    "Menggunakan data buku nyata dari OpenLibrary API.",
    "Menyimpan interaksi pengguna melalui Wishlist dan SearchHistory.",
    "Menghasilkan output AI yang terstruktur sehingga mudah ditampilkan.",
    "Menyediakan fitur pendukung seperti login, register, feedback, pesan admin, dan halaman favorit.",
]:
    add_bullet(item)

add_heading("5.4 Keterbatasan Aplikasi", 2)
for item in [
    "Rekomendasi belum sepenuhnya personal karena belum menghitung kemiripan antar pengguna atau antar buku.",
    "Ringkasan AI bergantung pada API eksternal dan koneksi internet.",
    "Kualitas ringkasan bergantung pada kemampuan model dan kejelasan judul buku yang dimasukkan.",
    "Jika AI mengembalikan JSON tidak valid, proses parsing dapat gagal dan sistem menampilkan error.",
    "SearchHistory sudah disimpan, tetapi belum dimanfaatkan sebagai fitur rekomendasi personal.",
]:
    add_bullet(item)

add_heading("5.5 Rencana Pengembangan", 2)
for item in [
    "Menambahkan rekomendasi personal berdasarkan riwayat pencarian dan wishlist pengguna.",
    "Menggunakan content-based filtering dengan fitur judul, author, kategori, dan deskripsi buku.",
    "Menambahkan rating dan review agar sinyal rekomendasi lebih kaya.",
    "Menambahkan validasi output AI yang lebih kuat agar sistem tetap stabil saat response tidak sesuai format.",
    "Menambahkan evaluasi kualitas rekomendasi menggunakan precision, recall, atau kuesioner kepuasan pengguna.",
]:
    add_bullet(item)
body.append(page_break())

add_heading("BAB VI PENUTUP", 1)
add_heading("6.1 Kesimpulan", 2)
add_para(
    "BookAI berhasil dijadikan contoh aplikasi berbasis kecerdasan buatan untuk mata kuliah Kecerdasan Buatan. "
    "Aplikasi ini menerapkan dua konsep AI utama, yaitu sistem rekomendasi populer berbasis data wishlist dan ringkasan buku berbasis Large Language Model. "
    "Dengan integrasi Django, MySQL, OpenLibrary API, dan Groq AI, BookAI mampu membantu pengguna mencari buku, menyimpan favorit, melihat buku populer, dan memahami gambaran isi buku melalui ringkasan otomatis."
)
add_para(
    "Algoritma rekomendasi pada BookAI bekerja dengan menghitung jumlah wishlist untuk menentukan buku populer. "
    "Algoritma ringkasan AI bekerja dengan mengambil judul buku, menyusun prompt, meminta model AI menghasilkan JSON, memproses hasil JSON, menyimpan hasil ke database, dan menampilkan ringkasan kepada pengguna. "
    "Walaupun belum menggunakan model machine learning yang dilatih sendiri, penerapan AI pada project ini sudah relevan karena memanfaatkan sistem rekomendasi dan NLP generatif pada kasus nyata."
)

add_heading("6.2 Saran", 2)
for item in [
    "Mengembangkan rekomendasi personal agar hasil lebih sesuai dengan minat masing-masing pengguna.",
    "Memanfaatkan SearchHistory sebagai input tambahan untuk sistem rekomendasi.",
    "Menambahkan dataset kategori buku agar content-based filtering lebih kuat.",
    "Menambahkan mekanisme retry dan validasi schema untuk hasil JSON dari AI.",
    "Melakukan pengujian kepada pengguna untuk menilai kualitas ringkasan dan rekomendasi.",
]:
    add_bullet(item)
body.append(page_break())

add_heading("DAFTAR PUSTAKA", 1)
add_para("Daftar pustaka berikut menggunakan referensi yang sudah tersedia pada file BookAI_Referensi_Mendeley.ris dan references_crossref_raw.json. Jumlah referensi yang digunakan adalah 12 sumber, sehingga memenuhi ketentuan minimal 10 referensi.")
for i, item in enumerate(refs, start=1):
    text = f"[{i}] {ref_apa(item)}"
    body.append(paragraph(text))
    md.append(f"{text}\n")


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
    <w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr>
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
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:before="160" w:after="80"/></w:pPr>
    <w:rPr><w:b/><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/></w:rPr>
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

OUT_MD.write_text("\n".join(md), encoding="utf-8")

with ZipFile(OUT_DOCX, "w", ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types_xml)
    z.writestr("_rels/.rels", rels_xml)
    z.writestr("word/document.xml", document_xml)
    z.writestr("word/styles.xml", styles_xml)
    z.writestr("word/_rels/document.xml.rels", doc_rels_xml)

print(OUT_DOCX.resolve())
print(OUT_MD.resolve())
