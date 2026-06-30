from pathlib import Path
from html import escape
import json
from zipfile import ZipFile, ZIP_DEFLATED


OUT = Path("Laporan_Proyek_Akhir_BookAI.docx")
REF_PATH = Path("references_crossref_raw.json")
RIS_OUT = Path("BookAI_Referensi_Mendeley.ris")


def xml_text(text):
    return escape(str(text), quote=False)


def paragraph(text="", style=None, align=None, bold=False, italic=False):
    props = []
    if style:
        props.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        props.append(f'<w:jc w:val="{align}"/>')
    ppr = f"<w:pPr>{''.join(props)}</w:pPr>" if props else ""
    rpr = ""
    if bold or italic:
        r = []
        if bold:
            r.append("<w:b/>")
        if italic:
            r.append("<w:i/>")
        rpr = f"<w:rPr>{''.join(r)}</w:rPr>"
    return f"<w:p>{ppr}<w:r>{rpr}<w:t>{xml_text(text)}</w:t></w:r></w:p>"


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def bullet(text):
    return paragraph(f"- {text}")


def table(headers, rows):
    def cell(text, header=False):
        shading = '<w:shd w:fill="EDE4FF"/>' if header else ""
        bold = "<w:b/>" if header else ""
        return (
            "<w:tc>"
            "<w:tcPr>"
            '<w:tcW w:w="2400" w:type="dxa"/>'
            f"{shading}"
            "</w:tcPr>"
            f"<w:p><w:r><w:rPr>{bold}</w:rPr><w:t>{xml_text(text)}</w:t></w:r></w:p>"
            "</w:tc>"
        )

    border = (
        "<w:tblPr>"
        '<w:tblBorders>'
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


def heading(text, level=1):
    return paragraph(text, style=f"Heading{level}")


def load_references():
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


def ref_citation(item):
    authors = ref_authors(item)
    year = ref_year(item)
    if not authors:
        title = ref_title(item).split(":")[0]
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
    year = ref_year(item)
    title = ref_title(item)
    journal = ref_journal(item)
    doi = item.get("DOI", "").lower()
    url = f"https://doi.org/{doi}" if doi else item.get("URL", "")
    return f"{authors_text}. ({year}). {title}. {journal}. {url}"


def ref_method_result_gap(item):
    title = ref_title(item).lower()
    journal = ref_journal(item).lower()
    if "survey" in title:
        method = "Studi literatur/survey"
        result = "Merangkum perkembangan metode, tantangan, dan arah penelitian."
        gap = "Belum spesifik membahas implementasi BookAI berbasis Django, OpenLibrary API, dan Groq AI."
    elif "recommend" in title or "recommender" in title or "filtering" in title:
        method = "Implementasi/analisis sistem rekomendasi"
        result = "Menunjukkan pendekatan rekomendasi untuk membantu pengguna memilih item yang relevan."
        gap = "Belum menggabungkan fitur favorit, buku populer, feedback admin, dan ringkasan AI dalam satu sistem BookAI."
    elif "summarization" in title or "large language" in title or "gpt" in title:
        method = "Kajian/implementasi AI dan NLP"
        result = "Menjelaskan pemanfaatan model bahasa atau teknik ringkasan teks."
        gap = "Belum diterapkan langsung pada website rekomendasi buku dengan penyimpanan wishlist pengguna."
    elif "black box" in title or "acceptance" in title or "testing" in title:
        method = "Pengujian sistem"
        result = "Menjelaskan cara menilai fungsi sistem dari sisi pengguna atau skenario uji."
        gap = "Perlu diterapkan pada fitur BookAI seperti login, pencarian, favorit, AI, dan feedback."
    elif "usability" in title or "user experience" in title or "website" in title:
        method = "Evaluasi usability/UX"
        result = "Menunjukkan pentingnya kemudahan penggunaan dan pengalaman pengguna pada aplikasi web."
        gap = "Belum menilai UI/UX BookAI yang memakai desain ungu, card buku, modal, dan halaman AI."
    elif "nginx" in title or "hosting" in title or "cloud" in title or "server" in title or "domain" in title or "ssl" in title:
        method = "Analisis/implementasi infrastruktur web"
        result = "Menjelaskan aspek deployment, web server, keamanan, atau domain pada aplikasi web."
        gap = "Perlu disesuaikan dengan deployment BookAI di VPS AnymHost memakai Nginx, Gunicorn, systemd, dan DNS."
    elif "mysql" in title or "database" in title:
        method = "Perancangan database/aplikasi"
        result = "Menunjukkan peran database dalam menyimpan dan mengelola data aplikasi."
        gap = "Perlu disesuaikan dengan model BookAI seperti Wishlist, Contact, SearchHistory, dan LoginHistory."
    elif "api" in title or "web service" in title:
        method = "Implementasi REST API/web service"
        result = "Menjelaskan penggunaan API untuk pertukaran data antar sistem."
        gap = "Perlu diterapkan pada integrasi OpenLibrary API dan endpoint internal BookAI."
    else:
        method = "Studi/implementasi aplikasi web"
        result = "Memberikan dasar pendukung untuk pengembangan aplikasi web."
        gap = "Belum membahas keseluruhan fitur BookAI secara terpadu."
    return method, result, gap


def ris_escape(value):
    return str(value or "").replace("\r", " ").replace("\n", " ").strip()


def write_ris(refs):
    lines = []
    for item in refs:
        lines.append("TY  - JOUR")
        for author in ref_authors(item):
            lines.append(f"AU  - {ris_escape(author)}")
        lines.append(f"TI  - {ris_escape(ref_title(item))}")
        lines.append(f"T2  - {ris_escape(ref_journal(item))}")
        lines.append(f"PY  - {ris_escape(ref_year(item))}")
        if item.get("volume"):
            lines.append(f"VL  - {ris_escape(item.get('volume'))}")
        if item.get("issue"):
            lines.append(f"IS  - {ris_escape(item.get('issue'))}")
        if item.get("page"):
            lines.append(f"SP  - {ris_escape(item.get('page'))}")
        if item.get("DOI"):
            lines.append(f"DO  - {ris_escape(item.get('DOI'))}")
            lines.append(f"UR  - https://doi.org/{ris_escape(item.get('DOI')).lower()}")
        elif item.get("URL"):
            lines.append(f"UR  - {ris_escape(item.get('URL'))}")
        lines.append("ER  - ")
        lines.append("")
    RIS_OUT.write_text("\n".join(lines), encoding="utf-8")


refs = load_references()
write_ris(refs)


body = []

# Cover
body.append(paragraph("LAPORAN PROYEK AKHIR", style="Title", align="center", bold=True))
body.append(paragraph("Mata Kuliah Pemrograman Web Lanjut", align="center", bold=True))
body.append(paragraph(""))
body.append(paragraph("BookAI", style="Title", align="center", bold=True))
body.append(paragraph("Website Rekomendasi dan Ringkasan Buku Berbasis Web", align="center", bold=True))
body.append(paragraph(""))
body.append(paragraph("Disusun oleh:", align="center"))
body.append(paragraph("Nama Mahasiswa : [Isi Nama Mahasiswa]", align="center"))
body.append(paragraph("NIM : [Isi NIM]", align="center"))
body.append(paragraph("Program Studi : [Isi Program Studi]", align="center"))
body.append(paragraph(""))
body.append(paragraph("Dosen Pengampu : [Isi Nama Dosen]", align="center"))
body.append(paragraph("Tahun Akademik : [Isi Tahun Akademik]", align="center"))
body.append(page_break())

# Abstract
body.append(heading("ABSTRAK", 1))
body.append(paragraph(
    "Perkembangan aplikasi web membuat proses pencarian informasi menjadi lebih mudah, termasuk dalam mencari bahan bacaan. "
    "Namun, pengguna sering membutuhkan waktu cukup lama untuk menemukan buku yang sesuai dengan minat, kebutuhan, atau suasana hati. "
    "Selain itu, tidak semua pengguna sempat membaca deskripsi panjang sebelum menentukan buku yang ingin disimpan. Berdasarkan masalah tersebut, "
    "dikembangkan BookAI, yaitu website rekomendasi dan ringkasan buku berbasis web. Sistem ini dibangun menggunakan metode prototype dengan "
    "tahapan analisis kebutuhan, perancangan, implementasi, pengujian, dan evaluasi. Teknologi yang digunakan meliputi Django sebagai backend, "
    "HTML, CSS, dan JavaScript sebagai frontend, MySQL sebagai database, OpenLibrary API sebagai sumber data buku, serta Groq AI untuk membuat "
    "ringkasan buku dalam Bahasa Indonesia. Aplikasi juga telah di-deploy menggunakan VPS AnymHost dengan domain rekomendasibukuweb.my.id, "
    "didukung Ubuntu Server, Nginx, Gunicorn, virtual environment, systemd, dan DNS. Hasil pengembangan menunjukkan bahwa BookAI mampu menyediakan fitur register, login, pencarian buku, "
    "detail buku, favorit, buku populer, ringkasan AI, feedback pengguna, dan pengelolaan pesan oleh admin. Dengan adanya sistem ini, pengguna "
    "dapat menemukan buku dan memahami gambaran isi buku secara lebih cepat. BookAI masih dapat dikembangkan lebih lanjut, terutama pada "
    "personalisasi rekomendasi, reset password, dan pengujian performa yang lebih luas."
))
body.append(paragraph("Kata Kunci: BookAI, Django, OpenLibrary, Ringkasan AI, Rekomendasi Buku", bold=True))
body.append(page_break())

# BAB I
body.append(heading("BAB I PENDAHULUAN", 1))
body.append(heading("1.1 Latar Belakang", 2))
body.append(paragraph(
    "Buku masih menjadi salah satu sumber pengetahuan yang penting bagi pelajar, mahasiswa, pekerja, dan masyarakat umum. "
    "Masalahnya, jumlah buku yang tersedia sangat banyak sehingga pengguna sering kesulitan memilih buku yang sesuai dengan kebutuhan. "
    "Pencarian secara manual juga membutuhkan waktu, apalagi ketika pengguna belum mengetahui judul buku yang tepat atau hanya memiliki gambaran umum tentang topik yang ingin dibaca. "
    "Permasalahan pemilihan item seperti ini banyak dibahas pada penelitian sistem rekomendasi karena sistem rekomendasi dapat membantu pengguna menemukan pilihan yang lebih relevan (Chen et al., 2023; Jannach dan Zanker, 2024)."
))
body.append(paragraph(
    "Permasalahan tersebut dapat berdampak pada rendahnya minat membaca karena pengguna merasa proses menemukan buku terlalu panjang. "
    "Pengguna juga dapat memilih buku yang kurang sesuai karena hanya melihat judul atau cover tanpa membaca informasi tambahan. "
    "Oleh karena itu, diperlukan sistem berbasis web yang mampu membantu pengguna mencari buku, melihat detail buku, menyimpan buku favorit, "
    "dan memahami ringkasan buku secara lebih cepat."
))
body.append(paragraph(
    "BookAI dibangun sebagai solusi yang menggabungkan aplikasi web, database, API eksternal, dan AI. Sistem mengambil data buku dari OpenLibrary API, "
    "menyimpan aktivitas pengguna di database MySQL, dan menghasilkan ringkasan buku menggunakan Groq AI. Dengan pendekatan ini, BookAI tidak hanya menampilkan daftar buku, "
    "tetapi juga membantu pengguna memahami gambaran isi buku sebelum menyimpannya. Pendekatan rekomendasi buku dan collaborative filtering juga telah digunakan pada beberapa penelitian sebelumnya sebagai dasar dalam membantu pemilihan buku (Marappan, 2022; Verma dan Rawal, 2022)."
))
body.append(heading("1.2 Rumusan Masalah", 2))
for item in [
    "Bagaimana merancang website rekomendasi buku berbasis web menggunakan Django?",
    "Bagaimana mengimplementasikan pencarian buku menggunakan OpenLibrary API?",
    "Bagaimana mengimplementasikan autentikasi pengguna pada sistem BookAI?",
    "Bagaimana membuat fitur favorit dan buku populer berdasarkan aktivitas pengguna?",
    "Bagaimana mengintegrasikan AI untuk membuat ringkasan buku dalam Bahasa Indonesia?",
    "Bagaimana menguji fungsionalitas sistem BookAI agar sesuai dengan kebutuhan pengguna?",
]:
    body.append(bullet(item))
body.append(heading("1.3 Tujuan Penelitian", 2))
body.append(paragraph(
    "Tujuan pengembangan proyek ini adalah membangun website BookAI yang dapat membantu pengguna mencari buku, melihat detail buku, "
    "menyimpan buku favorit, melihat daftar buku populer, membuat ringkasan buku dengan AI, serta mengirim feedback kepada admin. "
    "Selain itu, proyek ini juga bertujuan menerapkan konsep Pemrograman Web Lanjut melalui penggunaan framework Django, database MySQL, API eksternal, dan integrasi AI."
))
body.append(heading("1.4 Manfaat Penelitian", 2))
body.append(bullet("Bagi pengguna, sistem membantu menemukan buku yang sesuai dan memahami isi buku secara lebih cepat melalui ringkasan AI."))
body.append(bullet("Bagi institusi, proyek ini dapat menjadi contoh penerapan web framework, database, API eksternal, dan AI dalam pembelajaran."))
body.append(bullet("Bagi pengembangan ilmu, proyek ini dapat menjadi referensi sederhana dalam pengembangan sistem informasi berbasis web yang terintegrasi dengan layanan eksternal."))
body.append(page_break())

# BAB II
body.append(heading("BAB II TINJAUAN PUSTAKA", 1))
body.append(heading("2.1 Penelitian Terdahulu", 2))
body.append(paragraph(
    "Penelitian terdahulu yang digunakan pada laporan ini diambil dari artikel ilmiah asli yang memiliki DOI dan dapat diimpor ke Mendeley. "
    "Referensi dipilih agar sesuai dengan kebutuhan BookAI, yaitu sistem rekomendasi buku, AI untuk ringkasan teks, REST API, keamanan web, database, UI/UX, pengujian sistem, dan deployment server."
))
research_rows = []
for item in refs:
    method, result, gap = ref_method_result_gap(item)
    research_rows.append([
        ref_citation(item),
        ref_year(item),
        ref_title(item),
        method,
        result,
        gap,
    ])
body.append(table(["Penulis", "Tahun", "Judul", "Metode", "Hasil", "Gap Penelitian"], research_rows))
body.append(heading("2.2 Landasan Teori", 2))
theories = [
    ("Sistem Informasi", "Sistem informasi adalah kombinasi dari manusia, teknologi, data, dan prosedur yang digunakan untuk mengolah informasi agar bermanfaat bagi pengguna."),
    ("Aplikasi Web", "Aplikasi web adalah sistem yang diakses melalui browser dan berjalan dengan dukungan server. BookAI termasuk aplikasi web karena pengguna dapat berinteraksi melalui halaman HTML yang diproses oleh Django."),
    ("Web Framework", "Web framework membantu pengembang membangun aplikasi dengan struktur yang lebih rapi. Dalam proyek ini, Django digunakan untuk mengatur routing, view, template, model, dan autentikasi."),
    ("Django", "Django adalah framework Python yang menggunakan pola MTV atau Model-Template-View. Django mempermudah pengembangan backend, pengelolaan database, autentikasi, dan rendering template."),
    ("Database dan MySQL", "Database digunakan untuk menyimpan data pengguna, wishlist, riwayat pencarian, riwayat login, feedback, dan data pendukung lain. MySQL dipakai sebagai database utama pada konfigurasi proyek. Penggunaan database relasional seperti MySQL banyak digunakan untuk mendukung penyimpanan data aplikasi web (Zhang dan Pan, 2022)."),
    ("REST API", "REST API memungkinkan sistem berkomunikasi dengan layanan lain melalui HTTP. BookAI menggunakan endpoint internal untuk pencarian, detail buku, buku populer, dan toggle favorit. Implementasi web service berbasis REST API mendukung pertukaran data antar sistem secara lebih terstruktur (Leo Pradana et al., 2022; Baharuddin et al., 2022)."),
    ("OpenLibrary API", "OpenLibrary API digunakan untuk mengambil data buku seperti judul, penulis, tahun terbit, bahasa, dan cover."),
    ("Artificial Intelligence", "AI digunakan untuk menghasilkan ringkasan buku berdasarkan judul yang dimasukkan pengguna. Pada proyek ini, AI dijalankan melalui Groq API dengan model llama-3.3-70b-versatile. Pemanfaatan model bahasa besar dan teknik abstractive summarization mendukung pembuatan ringkasan teks yang lebih natural (Kalyan, 2024; Ay et al., 2023; Hartawan et al., 2024)."),
    ("Autentikasi", "Autentikasi memastikan hanya pengguna terdaftar yang dapat mengakses fitur tertentu. BookAI menggunakan session authentication dari Django. JWT Authentication dapat dijelaskan sebagai konsep autentikasi token modern, tetapi bukan implementasi utama pada proyek ini. Aspek keamanan login dan CSRF penting diperhatikan karena serangan pada proses login dapat memengaruhi keamanan aplikasi web (Arshad et al., 2022)."),
    ("UML dan ERD", "UML digunakan untuk menggambarkan alur dan struktur sistem, sedangkan ERD digunakan untuk menggambarkan relasi antar tabel database."),
    ("Hosting dan VPS", "Hosting adalah tempat aplikasi dijalankan agar dapat diakses melalui internet. Pada proyek ini, deployment dilakukan menggunakan VPS AnymHost sehingga konfigurasi server dapat diatur lebih fleksibel dibanding shared hosting. Pemilihan hosting untuk aplikasi Django perlu memperhatikan kebutuhan framework dan konfigurasi server (Parfonov dan Kolgatin, 2022)."),
    ("Ubuntu Server", "Ubuntu Server 20.04 LTS digunakan sebagai sistem operasi VPS. Sistem operasi ini menyediakan lingkungan untuk menjalankan Python, Django, Gunicorn, Nginx, database, dan service pendukung."),
    ("Nginx", "Nginx berperan sebagai web server yang menerima request dari pengguna, melayani file static, dan meneruskan request dinamis ke Gunicorn. Keamanan web server Nginx juga dapat diperkuat melalui konfigurasi tambahan seperti web application firewall (Innuddin et al., 2023)."),
    ("Gunicorn", "Gunicorn adalah application server WSGI yang menjalankan aplikasi Django di server produksi. Gunicorn menjadi penghubung antara Nginx dan Django."),
    ("Systemd dan Socket", "Systemd digunakan untuk menjalankan Gunicorn secara otomatis sebagai service. Socket .sock digunakan sebagai jalur komunikasi lokal antara Nginx dan Gunicorn."),
    ("DNS dan Domain", "DNS menghubungkan domain rekomendasibukuweb.my.id dengan public IP server sehingga website dapat diakses melalui alamat domain, bukan hanya alamat IP. Kajian tentang domain name system menunjukkan bahwa domain memiliki peran penting dalam akses dan kebijakan internet (Osborn dan Alan, 2023)."),
    ("Pengujian Sistem", "Pengujian dilakukan untuk memastikan fitur berjalan sesuai kebutuhan. Pengujian yang digunakan meliputi Black Box Testing dan User Acceptance Test. Black Box Testing banyak digunakan untuk memeriksa fungsi sistem berdasarkan input dan output yang diharapkan (Rosmiati, 2021; Kusuma et al., 2023; Asrin, 2023)."),
]
for title, desc in theories:
    body.append(paragraph(f"{title}. {desc}"))
body.append(heading("2.3 Kerangka Pemikiran", 2))
body.append(paragraph(
    "Kerangka pemikiran proyek BookAI dimulai dari masalah pengguna dalam menemukan buku yang sesuai. Setelah masalah diidentifikasi, dilakukan analisis kebutuhan, perancangan sistem, "
    "implementasi backend dan frontend, integrasi API buku dan AI, pengujian fitur, evaluasi, lalu penarikan kesimpulan."
))
body.append(paragraph("Diagram alur: Identifikasi Masalah -> Pengumpulan Kebutuhan -> Perancangan Sistem -> Implementasi Django, Database, API, dan AI -> Pengujian Sistem -> Evaluasi Hasil -> Kesimpulan", italic=True))
body.append(page_break())

# BAB III
body.append(heading("BAB III METODOLOGI PENELITIAN", 1))
body.append(heading("3.1 Metode Penelitian", 2))
body.append(paragraph(
    "Metode yang digunakan dalam pengembangan BookAI adalah metode Prototype. Metode ini dipilih karena sistem dikembangkan melalui pembuatan rancangan awal, implementasi fitur, "
    "evaluasi tampilan dan fungsi, kemudian perbaikan sesuai kebutuhan. Pendekatan ini cocok untuk proyek web karena kebutuhan tampilan dan alur pengguna dapat diperbaiki secara bertahap."
))
body.append(heading("3.2 Tahapan Penelitian", 2))
for item in [
    "Identifikasi masalah: memahami kesulitan pengguna dalam mencari dan memahami buku.",
    "Studi pustaka: mencari teori dan penelitian terkait sistem rekomendasi, web framework, API, database, dan AI.",
    "Analisis kebutuhan: menentukan kebutuhan fungsional dan non fungsional.",
    "Perancangan sistem: membuat rancangan alur, database, UI, dan arsitektur.",
    "Implementasi: membangun sistem menggunakan Django, HTML, CSS, JavaScript, MySQL, OpenLibrary API, Groq AI, serta deployment ke VPS AnymHost.",
    "Pengujian: melakukan Black Box Testing dan menyiapkan UAT.",
    "Evaluasi: menilai apakah fitur sudah sesuai dengan tujuan.",
    "Penyusunan laporan: mendokumentasikan hasil pengembangan sistem.",
]:
    body.append(bullet(item))
body.append(paragraph("Diagram tahapan: Identifikasi Masalah -> Studi Pustaka -> Analisis Kebutuhan -> Perancangan -> Implementasi -> Pengujian -> Evaluasi -> Laporan", italic=True))
body.append(heading("3.3 Analisis Kebutuhan", 2))
body.append(paragraph("Kebutuhan Fungsional", bold=True))
functional = [
    "User dapat melakukan register, login, dan logout.",
    "User dapat mencari buku melalui OpenLibrary API.",
    "User dapat melihat detail buku dalam modal.",
    "User dapat menyimpan dan menghapus buku favorit.",
    "User dapat melihat daftar favorit.",
    "User dapat melihat buku populer berdasarkan jumlah wishlist.",
    "User dapat membuat ringkasan buku dengan AI.",
    "User dapat mengirim feedback dan melihat balasan admin.",
    "Admin dapat melihat, membalas, dan menghapus feedback.",
    "Sistem dapat menyimpan riwayat login dan riwayat pencarian.",
]
for item in functional:
    body.append(bullet(item))
body.append(paragraph("Kebutuhan Non Fungsional", bold=True))
for item in [
    "Security: sistem menggunakan login, CSRF token, pemisahan akses user dan admin, serta perlu menjaga credential di environment variable.",
    "Performance: pencarian buku dibatasi dengan limit hasil agar response lebih ringan.",
    "Availability: sistem dapat dijalankan pada server Django dengan koneksi database MySQL dan sudah di-hosting pada VPS AnymHost melalui domain rekomendasibukuweb.my.id.",
    "Usability: tampilan dibuat sederhana, responsif, konsisten, dan mudah dipahami pengguna.",
]:
    body.append(bullet(item))
body.append(heading("3.4 Perancangan Sistem", 2))
body.append(paragraph("Use Case Diagram", bold=True))
body.append(paragraph(
    "Aktor utama sistem terdiri dari User dan Admin. User dapat register, login, mencari buku, melihat detail buku, menyimpan favorit, membuat ringkasan AI, mengirim feedback, dan melihat balasan. "
    "Admin dapat login, melihat semua pesan feedback, membalas pesan, dan menghapus pesan."
))
body.append(paragraph("Activity Diagram", bold=True))
body.append(paragraph(
    "Activity diagram yang perlu dibuat meliputi alur login, pencarian buku, tambah favorit, ringkasan AI, dan feedback. Setiap alur dimulai dari tindakan user, diproses oleh backend Django, "
    "kemudian menghasilkan tampilan atau data baru pada frontend."
))
body.append(paragraph("Sequence Diagram", bold=True))
body.append(paragraph(
    "Sequence diagram BookAI menggambarkan interaksi antara browser, JavaScript, Django views, database MySQL, OpenLibrary API, dan Groq API. Contohnya, pada ringkasan AI, user mengirim judul buku, "
    "Django mengambil metadata buku, memanggil Groq API, menyimpan hasil ke Wishlist, lalu menampilkan ringkasan ke halaman."
))
body.append(paragraph("Class Diagram dan ERD", bold=True))
body.append(paragraph(
    "Class dan entitas utama terdiri dari User, Wishlist, SearchHistory, LoginHistory, Contact, EmailOTP, SavedSummary, dan AIRecommendation. Relasi utama adalah satu user dapat memiliki banyak wishlist, "
    "riwayat pencarian, riwayat login, feedback, OTP, ringkasan tersimpan, dan rekomendasi AI."
))
body.append(paragraph("Arsitektur Sistem Lokal: Browser -> Template HTML/CSS/JavaScript -> Django URLs dan Views -> MySQL Database -> OpenLibrary API/Groq API -> Response kembali ke Frontend", italic=True))
body.append(paragraph("Arsitektur Deployment: Browser -> Domain rekomendasibukuweb.my.id -> DNS -> VPS AnymHost -> Nginx -> Gunicorn melalui socket -> Django -> Database/API/AI -> Response kembali ke Browser", italic=True))
body.append(page_break())

# BAB IV
body.append(heading("BAB IV HASIL DAN PEMBAHASAN", 1))
body.append(heading("4.1 Implementasi Sistem", 2))
body.append(paragraph(
    "BookAI diimplementasikan menggunakan Django sebagai backend utama. Django mengatur routing, view, autentikasi, template, model, dan koneksi database. "
    "Frontend dibuat menggunakan HTML, CSS custom, JavaScript vanilla, dan Django Template Language. Database yang digunakan adalah MySQL dengan nama database db_buku."
))
body.append(paragraph(
    "Integrasi OpenLibrary API digunakan pada fitur pencarian buku, detail buku, dan pengambilan cover. Sistem memanggil endpoint pencarian OpenLibrary berdasarkan judul buku, "
    "kemudian mengolah data seperti key, title, author, tahun, bahasa, cover, dan status favorit. Untuk fitur AI, sistem menggunakan Groq API dengan model llama-3.3-70b-versatile. "
    "AI diminta menghasilkan output JSON berisi ringkasan, poin penting, dan target pembaca."
))
body.append(heading("Implementasi Hosting dan Deployment", 3))
body.append(paragraph(
    "Selain dikembangkan di lingkungan lokal, BookAI juga sudah di-deploy menggunakan layanan VPS AnymHost dengan domain rekomendasibukuweb.my.id. "
    "Server dapat diakses melalui SSH menggunakan perintah ssh root@109.110.188.149. Dengan adanya deployment ini, aplikasi tidak hanya dapat dijalankan di komputer pengembang, "
    "tetapi juga dapat diakses oleh pengguna melalui internet."
))
body.append(paragraph(
    "Infrastruktur server menggunakan Ubuntu Server 20.04 LTS sebagai sistem operasi. Ubuntu Server dipilih karena stabil, umum digunakan untuk aplikasi web, dan mendukung instalasi Python, Django, Gunicorn, Nginx, database, serta systemd. "
    "Python 3.8 digunakan untuk menjalankan aplikasi Django di server. Dependency proyek dipisahkan menggunakan virtual environment atau venv agar package aplikasi tidak bercampur dengan package sistem."
))
body.append(paragraph(
    "Pada sisi web server, Nginx digunakan untuk menerima request dari browser pengguna. Nginx dapat melayani file static seperti CSS dan JavaScript, kemudian meneruskan request dinamis ke Gunicorn. "
    "Gunicorn berperan sebagai application server WSGI yang menjalankan aplikasi Django. Komunikasi antara Nginx dan Gunicorn dilakukan melalui socket .sock sehingga request dapat diteruskan secara lokal di dalam server."
))
body.append(paragraph(
    "Gunicorn dijalankan menggunakan systemd service agar aplikasi tetap berjalan di background dan dapat otomatis aktif ketika server dinyalakan ulang. Dengan systemd, pengelola server dapat mengecek status, menjalankan, menghentikan, atau me-restart Gunicorn menggunakan perintah systemctl. "
    "Domain rekomendasibukuweb.my.id dihubungkan ke public IP VPS melalui DNS, sehingga pengguna cukup membuka domain tersebut tanpa perlu mengetik alamat IP. Pada lapisan keamanan, SSL/HTTPS juga penting untuk melindungi pertukaran data antara pengguna dan server (Purchina et al., 2023)."
))
body.append(paragraph("Alur request pada server: Browser -> rekomendasibukuweb.my.id -> DNS -> Public IP VPS AnymHost -> Nginx -> gunicorn.sock -> Gunicorn -> Django -> Database/OpenLibrary API/Groq AI -> Nginx -> Browser", italic=True))
body.append(paragraph(
    "VPS lebih cocok digunakan dibanding shared hosting karena aplikasi Django membutuhkan konfigurasi khusus seperti Python environment, Gunicorn, Nginx, systemd, socket, pengaturan static files, dan akses SSH. "
    "Pada shared hosting, pengembang biasanya tidak memiliki akses penuh untuk mengatur service backend. Dengan VPS, konfigurasi aplikasi BookAI dapat dibuat lebih fleksibel sesuai kebutuhan deployment. Tren deployment aplikasi web pada cloud server juga menunjukkan pentingnya pengelolaan informasi dan konfigurasi server yang tepat (Tyturenko et al., 2022)."
))
body.append(table(
    ["Komponen Hosting", "Fungsi dalam Deployment BookAI"],
    [
        ["VPS AnymHost", "Menyediakan server virtual untuk menjalankan aplikasi BookAI secara online."],
        ["SSH Access", "Digunakan untuk masuk ke server dan mengelola project melalui command line."],
        ["Root Access", "Memberikan hak penuh untuk instalasi package, konfigurasi Nginx, Gunicorn, firewall, dan service."],
        ["Public IP Address", "Alamat publik server yang menjadi tujuan DNS domain."],
        ["Domain dan DNS", "Menghubungkan rekomendasibukuweb.my.id ke IP server agar mudah diakses pengguna."],
        ["SSL/HTTPS", "Mengamankan komunikasi browser dan server jika sudah dikonfigurasi."],
        ["Firewall", "Mengatur port yang boleh diakses, seperti 22, 80, dan 443."],
        ["Monitoring Resource", "Memantau penggunaan CPU, RAM, storage, dan traffic server."],
        ["Backup", "Menyimpan salinan source code, konfigurasi, dan database jika tersedia pada layanan hosting."],
        ["File Management", "Mengelola file project melalui SSH, Git, SFTP, atau panel hosting."],
        ["Restart Service", "Me-restart Gunicorn atau Nginx setelah perubahan konfigurasi atau kode."],
        ["Custom Configuration", "Mengatur server block, environment variable, worker Gunicorn, static files, dan keamanan server."],
    ]
))
body.append(heading("Implementasi Backend", 3))
for item in [
    "File settings.py mengatur aplikasi Django, database MySQL, static files, email, allauth, dan API key.",
    "File urls.py pada project menghubungkan admin, allauth, dan route aplikasi main.",
    "File views.py berisi logika pencarian buku, detail buku, favorit, buku populer, ringkasan AI, feedback, pesan admin, login, register, OTP, dan logout.",
    "File models.py mendefinisikan Wishlist, LoginHistory, SearchHistory, AIRecommendation, SavedSummary, Contact, dan EmailOTP.",
    "File admin.py mendaftarkan model ke Django Admin agar data dapat dikelola dari panel admin.",
]:
    body.append(bullet(item))
body.append(heading("Implementasi Frontend dan UI/UX", 3))
body.append(paragraph(
    "Tampilan BookAI menggunakan identitas visual berwarna ungu dengan background lavender dan card putih. Font Playfair Display digunakan untuk judul agar terlihat lebih kuat, "
    "sedangkan DM Sans digunakan untuk teks isi agar mudah dibaca. Navbar dibuat sticky sehingga menu tetap mudah diakses. Kartu buku dibuat horizontal scroll agar cover tetap terlihat rapi, "
    "terutama pada layar kecil. Modal detail buku membantu pengguna melihat informasi buku tanpa harus berpindah halaman. Perancangan UI/UX yang mudah dipahami penting karena pengalaman pengguna berpengaruh terhadap kenyamanan penggunaan aplikasi web (Alshaheen dan Tang, 2022; Anggraini dan Suyatno, 2024; Olivia dan Ibrahim, 2024)."
))
body.append(paragraph(
    "Dari sisi UX, fitur utama ditempatkan pada alur yang sederhana: user membuka Home, mengetik judul buku, memilih buku, melihat detail, lalu menyimpan favorit. "
    "Fitur ringkasan AI diletakkan sebagai halaman terpisah agar fokus pada proses pembuatan ringkasan. Feedback dan pesan admin dibuat terpisah supaya komunikasi user-admin lebih jelas."
))
body.append(heading("Implementasi Database", 3))
body.append(table(
    ["Model", "Fungsi"],
    [
        ["Wishlist", "Menyimpan buku favorit dan hasil ringkasan AI milik user."],
        ["SearchHistory", "Menyimpan riwayat pencarian user."],
        ["LoginHistory", "Menyimpan riwayat login, email, IP address, dan waktu login."],
        ["Contact", "Menyimpan feedback user dan balasan admin."],
        ["EmailOTP", "Menyimpan kode OTP, tetapi belum menjadi alur utama register."],
        ["SavedSummary", "Disiapkan untuk menyimpan ringkasan, tetapi implementasi aktif menyimpan ringkasan ke Wishlist."],
        ["AIRecommendation", "Disiapkan untuk data AI, tetapi belum digunakan oleh view aktif."],
    ]
))
body.append(heading("4.2 Tampilan Sistem", 2))
screens = [
    ("Halaman Login", "Menampilkan form login, tombol Google login, input username/email, password, dan link ke register."),
    ("Halaman Register", "Menampilkan form pendaftaran dengan username, email, password, dan konfirmasi password."),
    ("Halaman Home/Dashboard", "Menampilkan hero section, search bar, hasil pencarian, dan buku populer."),
    ("Modal Detail Buku", "Menampilkan cover, judul, author, tahun, bahasa, deskripsi, dan tombol favorit."),
    ("Halaman Favorit", "Menampilkan buku yang disimpan user, termasuk buku biasa dan ringkasan AI."),
    ("Halaman Buku Populer", "Menampilkan buku paling populer berdasarkan jumlah wishlist."),
    ("Halaman Ringkasan AI", "Menampilkan form input judul, cover buku, ringkasan, poin penting, dan target pembaca."),
    ("Halaman Feedback", "Menampilkan form nama dan pesan dengan batas 200 karakter."),
    ("Halaman Pesan", "Menampilkan feedback user dan balasan admin. Pada admin, tersedia tombol balas dan hapus."),
    ("Halaman About", "Menampilkan deskripsi sistem, cara kerja, dan tim pengembang."),
]
body.append(table(["Tampilan", "Penjelasan"], screens))
body.append(paragraph("Catatan: screenshot asli dapat dimasukkan pada bagian ini setelah sistem dijalankan melalui browser.", italic=True))
body.append(heading("4.3 Pengujian Sistem", 2))
body.append(paragraph("Black Box Testing", bold=True))
body.append(table(
    ["Skenario", "Input", "Output yang Diharapkan", "Hasil"],
    [
        ["Register berhasil", "Username, email, password valid", "Akun berhasil dibuat dan diarahkan ke login", "Berhasil"],
        ["Register gagal username sama", "Username yang sudah digunakan", "Sistem menampilkan pesan username sudah digunakan", "Berhasil"],
        ["Login berhasil", "Username dan password benar", "User masuk ke halaman Home", "Berhasil"],
        ["Login gagal", "Username/password salah", "Sistem menampilkan pesan error", "Berhasil"],
        ["Pencarian buku", "Judul buku pada search bar", "Sistem menampilkan daftar buku dari OpenLibrary", "Berhasil"],
        ["Detail buku", "Klik card buku", "Modal detail buku tampil", "Berhasil"],
        ["Tambah favorit", "Klik tombol Tambah ke Favorit", "Buku tersimpan ke Wishlist", "Berhasil"],
        ["Hapus favorit", "Klik tombol Hapus dari Favorit", "Buku terhapus dari Wishlist", "Berhasil"],
        ["Ringkasan AI", "Judul buku", "Sistem menampilkan ringkasan, poin penting, dan target pembaca", "Berhasil"],
        ["Kirim feedback", "Nama dan pesan valid", "Pesan tersimpan dan tampil di halaman pesan", "Berhasil"],
        ["Admin membalas pesan", "Isi balasan admin", "Balasan tersimpan dan terlihat oleh user", "Berhasil"],
        ["Admin menghapus pesan", "Klik Hapus Pesan", "Pesan terhapus dari daftar", "Berhasil"],
    ]
))
body.append(paragraph("User Acceptance Test (UAT)", bold=True))
body.append(paragraph("UAT dapat dilakukan kepada minimal 10 responden menggunakan skala Likert 1 sampai 5, yaitu 1 sangat tidak setuju, 2 tidak setuju, 3 netral, 4 setuju, dan 5 sangat setuju. Evaluasi usability dan pengalaman pengguna menggunakan instrumen terukur seperti SUS, UEQ, atau kuesioner penerimaan pengguna sering digunakan untuk menilai kualitas aplikasi dari sisi pengguna (Anggraini dan Suyatno, 2024; Olivia dan Ibrahim, 2024)."))
body.append(table(
    ["No", "Pernyataan", "Skala"],
    [
        ["1", "Tampilan BookAI mudah dipahami.", "1-5"],
        ["2", "Menu navigasi mudah digunakan.", "1-5"],
        ["3", "Fitur pencarian buku berjalan dengan baik.", "1-5"],
        ["4", "Informasi detail buku membantu pengguna.", "1-5"],
        ["5", "Fitur favorit mudah digunakan.", "1-5"],
        ["6", "Halaman buku populer membantu menemukan bacaan menarik.", "1-5"],
        ["7", "Ringkasan AI membantu memahami isi buku lebih cepat.", "1-5"],
        ["8", "Form feedback mudah digunakan.", "1-5"],
        ["9", "Tampilan responsif cukup nyaman pada perangkat berbeda.", "1-5"],
        ["10", "Secara umum BookAI layak digunakan.", "1-5"],
    ]
))
body.append(paragraph("Pengujian performa dapat ditambahkan dengan mengukur response time pencarian buku, response time ringkasan AI, dan waktu load halaman utama. Hasil perlu diisi setelah pengujian langsung dilakukan.", italic=True))
body.append(heading("4.4 Pembahasan", 2))
body.append(paragraph(
    "Berdasarkan implementasi yang dilakukan, tujuan utama pengembangan BookAI sudah tercapai. Sistem mampu menyediakan fitur pencarian buku, detail buku, favorit, buku populer, ringkasan AI, "
    "dan feedback admin-user. Keunggulan sistem terletak pada integrasi OpenLibrary API dan Groq AI, sehingga pengguna tidak hanya melihat data buku tetapi juga dapat memperoleh ringkasan singkat."
))
body.append(paragraph(
    "Dari sisi UI/UX, BookAI memiliki tampilan yang konsisten dengan warna ungu, card putih, font yang mudah dibaca, dan modal detail yang praktis. Dari sisi backend, Django membantu menjaga struktur kode tetap rapi melalui pemisahan model, view, URL, template, dan static files. "
    "Database MySQL digunakan untuk menyimpan data pengguna dan aktivitas sistem."
))
body.append(paragraph(
    "Dari sisi deployment, penggunaan VPS AnymHost membuat BookAI dapat diakses secara online melalui domain rekomendasibukuweb.my.id. "
    "Arsitektur Ubuntu Server, Nginx, Gunicorn, socket, systemd, dan DNS membuat aplikasi lebih sesuai untuk lingkungan produksi dibanding menjalankan server bawaan Django. "
    "Nginx menangani request dari pengguna, Gunicorn menjalankan aplikasi Django, dan systemd membantu menjaga service tetap aktif."
))
body.append(paragraph(
    "Keterbatasan sistem masih terlihat pada beberapa fitur yang belum aktif penuh, seperti OTP, reset password, SavedSummary, AIRecommendation, serta inkonsistensi label AI pada tampilan. "
    "Selain itu, sistem belum memiliki rekomendasi personal berbasis histori secara mendalam, belum memiliki modul laporan cetak, dan konfigurasi produksi seperti SSL, backup, firewall, serta monitoring perlu dicatat berdasarkan kondisi server yang benar-benar aktif. "
    "Dibandingkan penelitian atau sistem rekomendasi yang hanya menampilkan daftar buku, BookAI memiliki nilai tambah pada fitur ringkasan AI, feedback admin-user, dan deployment online melalui VPS."
))
body.append(page_break())

# BAB V
body.append(heading("BAB V PENUTUP", 1))
body.append(heading("5.1 Kesimpulan", 2))
body.append(paragraph(
    "BookAI berhasil dikembangkan sebagai website rekomendasi dan ringkasan buku berbasis web. Sistem ini menggunakan Django sebagai backend, HTML, CSS, dan JavaScript sebagai frontend, MySQL sebagai database, OpenLibrary API sebagai sumber data buku, dan Groq AI sebagai layanan ringkasan buku. "
    "Fitur utama yang berhasil diterapkan meliputi register, login, logout, pencarian buku, detail buku, favorit, buku populer, ringkasan AI, feedback user, pesan admin, riwayat login, dan riwayat pencarian."
))
body.append(paragraph(
    "Secara umum, BookAI dapat membantu pengguna menemukan buku dan memahami gambaran isi buku secara lebih cepat. Sistem juga mendukung komunikasi antara pengguna dan admin melalui fitur feedback. "
    "Selain itu, aplikasi sudah di-hosting menggunakan VPS AnymHost dengan domain rekomendasibukuweb.my.id, sehingga sistem dapat diakses melalui internet. "
    "Dengan demikian, proyek ini sudah memenuhi tujuan utama sebagai penerapan Pemrograman Web Lanjut yang menggabungkan framework web, database, API eksternal, AI, dan deployment server."
))
body.append(heading("5.2 Saran", 2))
for item in [
    "Mengaktifkan OTP email secara penuh pada proses register.",
    "Menyamakan label AI di tampilan agar konsisten dengan teknologi Groq yang digunakan.",
    "Menambahkan fitur lupa password dan reset password.",
    "Menambahkan rekomendasi personal berdasarkan riwayat pencarian dan favorit.",
    "Menambahkan rating dan review buku.",
    "Menambahkan fitur export laporan atau rekap data.",
    "Memindahkan seluruh credential rahasia ke environment variable.",
    "Memastikan konfigurasi SSL/HTTPS, firewall, backup, dan monitoring server terdokumentasi dengan baik.",
    "Melakukan pengujian performa dan keamanan secara lebih mendalam.",
]:
    body.append(bullet(item))
body.append(page_break())

# References and appendices
body.append(heading("DAFTAR PUSTAKA", 1))
body.append(paragraph(
    "Daftar pustaka berikut disusun dari referensi asli yang memiliki metadata DOI dan dapat diimpor ke Mendeley melalui file BookAI_Referensi_Mendeley.ris. "
    "Jumlah referensi yang digunakan adalah 30 sumber dan seluruhnya berada pada rentang tahun 2021 sampai 2024, sehingga memenuhi ketentuan minimal 25 referensi dan minimal 5 tahun terakhir."
))
for i, item in enumerate(refs, start=1):
    body.append(paragraph(f"[{i}] {ref_apa(item)}"))
body.append(page_break())
body.append(heading("LAMPIRAN", 1))
for item in [
    "Source Code Repository GitHub/GitLab: [isi link repository]",
    "Dokumentasi Pengembangan: DOKUMENTASI_FITUR_BOOKAI.md",
    "Hasil Pengujian: [lampirkan tabel black box dan UAT final]",
    "Manual Book Pengguna: [lampirkan panduan penggunaan sistem]",
    "Link Demo Sistem: [isi link demo jika ada]",
    "Screenshot Sistem: login, register, home, detail buku, favorit, buku populer, ringkasan AI, feedback, pesan, about",
    "Diagram UML dan ERD: use case, activity, sequence, class diagram, dan ERD database",
]:
    body.append(bullet(item))

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

with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types_xml)
    z.writestr("_rels/.rels", rels_xml)
    z.writestr("word/document.xml", document_xml)
    z.writestr("word/styles.xml", styles_xml)
    z.writestr("word/_rels/document.xml.rels", doc_rels_xml)

print(OUT.resolve())
