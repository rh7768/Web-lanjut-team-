import json
import requests
import re
from groq import Groq   
from urllib.parse import quote_plus

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import IntegrityError, transaction
from django.db.models import Q

from .models import Wishlist, SearchHistory, LoginHistory, Contact, EmailOTP
from django.contrib import messages
from django.utils import timezone
from django.conf import settings


# ======================
# STORAGE FAVORITE (for backward compatibility)
# ======================

favorite_books = []


LANGUAGE_NAMES = {
    'eng': 'English',
    'en': 'English',
    'ind': 'Indonesian',
    'id': 'Indonesian',
    'may': 'Malay',
    'msa': 'Malay',
    'fre': 'French',
    'fra': 'French',
    'ger': 'German',
    'deu': 'German',
    'spa': 'Spanish',
    'ita': 'Italian',
    'por': 'Portuguese',
    'dut': 'Dutch',
    'nld': 'Dutch',
    'jpn': 'Japanese',
    'kor': 'Korean',
    'chi': 'Chinese',
    'zho': 'Chinese',
    'ara': 'Arabic',
    'rus': 'Russian',
}


def _format_language(language):
    if isinstance(language, list):
        language = next((item for item in language if item), '')

    if not language:
        return ''

    language = str(language).strip()
    language_key = language.lower()

    if language_key in LANGUAGE_NAMES:
        return LANGUAGE_NAMES[language_key]

    if len(language) <= 3:
        return language.upper()

    return language.title()


def _openlibrary_doc_to_meta(item):
    if not item:
        return {}

    cover_id = item.get('cover_i')
    cover_url = ''
    if cover_id:
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

    authors = item.get('author_name') or []
    description = item.get('first_sentence')
    if isinstance(description, list):
        description = description[0] if description else ''

    return {
        'key': item.get('key', ''),
        'title': item.get('title', ''),
        'author': authors[0] if authors else '',
        'year': item.get('first_publish_year'),
        'language': _format_language(item.get('language')),
        'cover_url': cover_url,
        'description': description or 'Book from OpenLibrary API',
    }


def _cover_id_from_url(cover_url):
    if cover_url and 'id/' in cover_url:
        try:
            return int(cover_url.split('id/')[1].split('-')[0])
        except (TypeError, ValueError, IndexError):
            return None
    return None


def _score_openlibrary_doc(item, title='', book_key=''):
    score = 0
    item_title = (item.get('title') or '').strip().lower()
    wanted_title = (title or '').strip().lower()

    if book_key and item.get('key') == book_key:
        score += 50
    if wanted_title and item_title == wanted_title:
        score += 30
    elif wanted_title and wanted_title in item_title:
        score += 12

    if item.get('first_publish_year'):
        score += 8
    if item.get('language'):
        score += 8
    if item.get('cover_i'):
        score += 4
    if item.get('author_name'):
        score += 4

    return score


def _fetch_openlibrary_meta(title='', book_key=''):
    title = (title or '').strip()
    book_key = (book_key or '').strip()

    if not title and not book_key:
        return {}

    if title:
        url = (
            "https://openlibrary.org/search.json"
            f"?title={quote_plus(title)}&limit=5"
        )
    else:
        cleaned_key = book_key.replace('/works/', '')
        url = (
            "https://openlibrary.org/search.json"
            f"?q={quote_plus(cleaned_key)}&limit=5"
        )

    try:
        response = requests.get(url, timeout=8)
        if response.status_code != 200:
            return {}

        docs = response.json().get('docs', [])
        if not docs:
            return {}

        selected = max(
            docs,
            key=lambda item: _score_openlibrary_doc(item, title, book_key)
        )

        return _openlibrary_doc_to_meta(selected)

    except requests.RequestException:
        return {}


# ======================
# TOGGLE FAVORITE
# ======================

@require_POST
@login_required(login_url='login')
def toggle_favorite(request):

    data = json.loads(request.body)

    key = data.get('key')
    title = data.get('title', '')
    author = data.get('author', '')
    cover_url = data.get('cover_url', '')

    # Ambil cover_id dari cover_url jika ada
    cover_id = _cover_id_from_url(cover_url)

    # Cek apakah sudah ada di database
    existing = Wishlist.objects.filter(
        user=request.user,
        book_key=key
    ).first()

    # HAPUS FAVORITE
    if existing:
        existing.delete()
        favorite_books[:] = [b for b in favorite_books if b['key'] != key]
        
        return JsonResponse({
            'status': 'removed'
        })

    # TAMBAH FAVORITE
    Wishlist.objects.create(
        user=request.user,
        book_key=key,
        title=title,
        author=author,
        cover_id=cover_id
    )
    
    # Simpan juga di memory untuk backward compatibility
    data_to_add = data.copy()
    favorite_books.append(data_to_add)

    return JsonResponse({
        'status': 'added'
    })


# ======================
# API POPULAR BOOKS
# ======================

def popular_books(request):
    """
    Ambil buku populer berdasarkan jumlah wishlist (favorit)
    """
    limit = request.GET.get('limit', 6)
    include_detail = request.GET.get('detail') == '1'
    
    try:
        limit = int(limit)
        if limit > 100:
            limit = 100
    except:
        limit = 6

    # Ambil buku dengan wishlist terbanyak dari database
    from django.db.models import Count
    
    popular_wishlist = Wishlist.objects.values('book_key', 'title', 'author', 'cover_id').annotate(
        wishlist_count=Count('id')
    ).order_by('-wishlist_count')[:limit]

    books = []

    for item in popular_wishlist:
        cover_url = None
        if item['cover_id']:
            cover_url = f"https://covers.openlibrary.org/b/id/{item['cover_id']}-L.jpg"

        # Cek favorite dari database jika user login
        is_favorite = False
        if request.user.is_authenticated:
            is_favorite = Wishlist.objects.filter(
                user=request.user,
                book_key=item['book_key']
            ).exists()

        meta = {}
        if include_detail:
            meta = _fetch_openlibrary_meta(
                title=item['title'],
                book_key=item['book_key']
            )

        books.append({
            'key': item['book_key'],
            'title': item['title'],
            'author': meta.get('author') or item['author'],
            'year': meta.get('year'),
            'cover_url': meta.get('cover_url') or cover_url,
            'language': meta.get('language', ''),
            'description': meta.get('description') or 'Book from OpenLibrary API',
            'is_favorite': is_favorite,
            'wishlist_count': item['wishlist_count']
        })

    return JsonResponse({
        'books': books
    })


# ======================
# API SEARCH BOOKS
# ======================

def search_books(request):

    query = request.GET.get('q', '').strip()

    page = request.GET.get('page', 1)

    if not query:
        return JsonResponse({
            'books': [],
            'total': 0
        })

    # Simpan search history jika user login
    if request.user.is_authenticated:
        SearchHistory.objects.create(
            user=request.user,
            query=query
        )

    limit = 20

    # SEARCH HANYA BERDASARKAN JUDUL
    url = (
        f"https://openlibrary.org/search.json"
        f"?title={query}&page={page}&limit={limit}"
    )

    response = requests.get(url)

    books = []

    total = 0

    if response.status_code == 200:

        data = response.json()

        total = data.get('numFound', 0)

        for item in data.get('docs', []):

            cover_id = item.get('cover_i')

            cover_url = None

            if cover_id:
                cover_url = (
                    f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                )

            # Cek favorite dari database jika user login
            is_favorite = False
            if request.user.is_authenticated:
                is_favorite = Wishlist.objects.filter(
                    user=request.user,
                    book_key=item.get('key')
                ).exists()

            books.append({
                'key': item.get('key'),
                'title': item.get('title'),
                'author': item.get('author_name', ['Unknown'])[0],
                'year': item.get('first_publish_year'),
                'cover_url': cover_url,
                'language': _format_language(item.get('language')),
                'description': 'Book from OpenLibrary API',
                'is_favorite': is_favorite
            })

    return JsonResponse({
        'books': books,
        'total': total
    })


# ======================
# API BOOK DETAIL
# ======================

def book_detail(request):
    title = request.GET.get('title', '').strip()
    book_key = request.GET.get('key', '').strip()

    meta = _fetch_openlibrary_meta(title=title, book_key=book_key)

    return JsonResponse({
        'year': meta.get('year'),
        'language': meta.get('language', ''),
        'cover_url': meta.get('cover_url', ''),
        'author': meta.get('author', ''),
        'description': meta.get('description', ''),
    })


# ======================
# HOME
# ======================

def home(request):

    return render(request, 'home.html')

# ======================
# Ringkasan AI 
# ======================

@login_required(login_url='login')
def ringkasan_ai(request):

    summary = ""
    points = []
    targets = []
    book_title = ""
    cover_url = ""
    book_cover_id = None
    book_author = "AI Summary"
    book_year = ""
    book_language = ""

    if request.method == "POST":

        book_title = request.POST.get("judul", "").strip()

        # Ambil metadata buku dari OpenLibrary
        try:
            meta = _fetch_openlibrary_meta(title=book_title)
            cover_url = meta.get("cover_url", "")
            book_cover_id = _cover_id_from_url(cover_url)
            book_author = meta.get("author") or book_author
            book_year = meta.get("year") or ""
            book_language = meta.get("language", "")

        except Exception as e:
            print("ERROR COVER:", e)

        # Generate Ringkasan AI Gemini
    if book_title:

        try:

            client = Groq(
                api_key=settings.GROQ_API_KEY
            )

            prompt = f"""
        Buat ringkasan buku "{book_title}" dalam Bahasa Indonesia.

        Berikan output JSON VALID tanpa markdown.

        Format:

        {{
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
        }}
        """

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response.choices[0].message.content.strip()

            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

            print("RESPON GROQ:")
            print(content)

            data = json.loads(content)

            summary = data.get("ringkasan", "")
            points = data.get("poin_penting", [])
            targets = data.get("cocok_untuk", [])

            Wishlist.objects.update_or_create(
            user=request.user,
            book_key=f"ai-{book_title}",
            defaults={
            "title": book_title,
            "author": book_author,
            "cover_id": book_cover_id,
            "ai_summary": summary,
            "ai_points": points,
            "ai_targets": targets,
                }
            )

        except Exception as e:

            print("ERROR GROQ:", e)

            summary = f"Error Groq: {str(e)}"

    return render(
        request,
        "ringkasan_ai.html",
        {
            "summary": summary,
            "points": points,
            "targets": targets,
            "book_title": book_title,
            "cover_url": cover_url,
            "book_author": book_author,
            "book_year": book_year,
            "book_language": book_language,
        }
    )

# ======================
# POPULAR BOOKS PAGE
# ======================

@login_required(login_url='login')
def popular_books_page(request):

    return render(request, 'popular-books.html')


# ======================
# FAVORITES
# ======================

@login_required(login_url='login')
def favorites(request):
    # Ambil wishlist dari database
    wishlists = Wishlist.objects.filter(user=request.user).order_by('-created_at')
    
    # Convert ke format yang sama dengan api response
    favorites_data = []
    for wishlist in wishlists:
        cover_url = None
        if wishlist.cover_id:
            cover_url = f"https://covers.openlibrary.org/b/id/{wishlist.cover_id}-L.jpg"

        meta = _fetch_openlibrary_meta(
            title=wishlist.title,
            book_key=wishlist.book_key
        )

        if meta.get('cover_url') and not cover_url:
            cover_url = meta.get('cover_url')

        saved_author = (wishlist.author or '').strip()
        author = saved_author
        if not saved_author or saved_author in ('Unknown', 'AI Summary'):
            author = meta.get('author') or saved_author

        description = wishlist.ai_summary or meta.get('description') or 'Book from OpenLibrary API'
        
        favorites_data.append({
            'key': wishlist.book_key,
            'title': wishlist.title,
            'author': author,
            'year': meta.get('year') or '',
            'cover_url': cover_url,
            'language': meta.get('language') or '',
            'description': description,
            'saved_at': wishlist.created_at,

            'ai_summary': wishlist.ai_summary,
            'ai_points': wishlist.ai_points,
            'ai_targets': wishlist.ai_targets,
        })

    return render(request, 'favorites.html', {
        'favorites': favorites_data
    })

# ======================
# CONTACT
# ======================

@login_required(login_url='login')
def contact(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('message_list')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        message = request.POST.get('message', '').strip()

        # Ambil email dari akun yang sedang login
        email = (request.user.email or '').strip()

        # Hitung karakter (termasuk spasi)
        char_count = len(message) if message else 0

        if not name:
            messages.error(request, 'Nama wajib diisi.')
            return render(request, 'contact.html', {'name': name, 'message': message})

        if not message:
            messages.error(request, 'Pesan wajib diisi.')
            return render(request, 'contact.html', {'name': name, 'message': message})

        if char_count > 200:
            messages.error(request, f'Pesan terlalu panjang — maksimum 200 karakter (saat ini {char_count}).')
            return render(request, 'contact.html', {'name': name, 'message': message})

        contact_email = email or getattr(settings, 'DEFAULT_FROM_EMAIL', '') or 'no-reply@bookai.local'
        Contact.objects.create(
            user=request.user,
            name=name,
            email=contact_email,
            message=message
        )

        messages.success(request, f'Pesan dari {name} sudah masuk ke halaman Pesan.')

        # Redirect untuk menghindari resubmission
        return redirect('message_list')

    return render(request, 'contact.html')


# ======================
# MESSAGES
# ======================

def _is_admin_user(user):
    return user.is_staff or user.is_superuser


@login_required(login_url='login')
def message_list(request):
    if _is_admin_user(request.user):
        contacts = Contact.objects.select_related('user', 'replied_by').order_by('-created_at')
    else:
        filters = Q(user=request.user)
        if request.user.email:
            filters |= Q(user__isnull=True, email=request.user.email)
        contacts = Contact.objects.select_related('user', 'replied_by').filter(filters).order_by('-created_at')

    return render(request, 'messages.html', {
        'contacts': contacts,
        'is_admin_view': _is_admin_user(request.user),
    })


@require_POST
@login_required(login_url='login')
def reply_message(request, contact_id):
    if not _is_admin_user(request.user):
        messages.error(request, 'Hanya admin yang bisa membalas pesan.')
        return redirect('message_list')

    contact = get_object_or_404(Contact, pk=contact_id)
    reply = request.POST.get('admin_reply', '').strip()

    if not reply:
        messages.error(request, 'Balasan tidak boleh kosong.')
        return redirect('message_list')

    contact.admin_reply = reply
    contact.replied_by = request.user
    contact.replied_at = timezone.now()
    contact.save(update_fields=['admin_reply', 'replied_by', 'replied_at'])
    messages.success(request, 'Balasan admin sudah disimpan.')
    return redirect('message_list')


@require_POST
@login_required(login_url='login')
def delete_message(request, contact_id):
    if not _is_admin_user(request.user):
        messages.error(request, 'Hanya admin yang bisa menghapus pesan.')
        return redirect('message_list')

    contact = get_object_or_404(Contact, pk=contact_id)
    contact.delete()
    messages.success(request, 'Pesan sudah dihapus.')
    return redirect('message_list')


# ======================
# ABOUT US
# ======================

def about(request):
    return render(request, 'about.html')


# ======================
# LOGIN
# ======================

def login_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Ambil IP address dari request
            ip_address = request.META.get('REMOTE_ADDR', '')
            
            # Simpan login history ke database
            LoginHistory.objects.create(
                user=user,
                email=user.email,
                ip_address=ip_address
            )

            return redirect('home')

        registered_user = User.objects.filter(username__iexact=username).first()
        if (
            registered_user
            and not registered_user.is_active
            and registered_user.check_password(password)
        ):
            messages.error(
                request,
                'Akun belum aktif. Silakan verifikasi email terlebih dahulu.'
            )
        else:
            messages.error(request, 'Username atau password salah.')

    return render(request, 'auth/login.html', {
        'username': request.POST.get('username', '') if request.method == 'POST' else ''
    })


# ======================
# REGISTER
# ======================

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1') or request.POST.get('password', '')
        password2 = request.POST.get('password2') or password1
        form_data = {
            'username': username,
            'email': email,
        }

        # Validasi sederhana
        if not username or not email or not password1 or not password2:
            return render(request, 'auth/register.html', {
                **form_data,
                'error': 'Lengkapi semua field.',
            })

        if password1 != password2:
            return render(request, 'auth/register.html', {
                **form_data,
                'error': 'Konfirmasi password tidak sama.',
            })

        # Pastikan email unik
        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'auth/register.html', {
                **form_data,
                'error': 'Email sudah terdaftar. Gunakan email lain.',
            })

        # Pastikan username unik
        if User.objects.filter(username__iexact=username).exists():
            return render(request, 'auth/register.html', {
                **form_data,
                'error': 'Username sudah digunakan.',
            })

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )
        except IntegrityError:
            return render(request, 'auth/register.html', {
                **form_data,
                'error': 'Username sudah digunakan. Silakan pilih username lain.',
            })

        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])

        messages.success(
            request,
            'Akun berhasil dibuat. Silakan login.'
        )

        return redirect('login')

    return render(request, 'auth/register.html')


# ======================
# VERIFY OTP
# ======================

def verify_otp(request):

    print("SESSION OTP:", request.session.get('pending_user_id'))

    user_id = request.session.get('pending_user_id')

    if not user_id:
        return redirect('register')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':

        otp = ''.join([
            request.POST.get('otp1', ''),
            request.POST.get('otp2', ''),
            request.POST.get('otp3', ''),
            request.POST.get('otp4', ''),
            request.POST.get('otp5', ''),
            request.POST.get('otp6', '')
        ])

        saved_otp = EmailOTP.objects.filter(
            user=user
        ).order_by('-created_at').first()

        if saved_otp and saved_otp.otp == otp:

            user.is_active = True
            user.save()

            saved_otp.delete()

            messages.success(
                request,
                'Email berhasil diverifikasi.'
            )

            return redirect('login')

        messages.error(request, 'OTP salah.')

    return render(
        request,
        'auth/verify_otp.html',
        {
            'email': user.email
        }
    )

# ======================
# LOGOUT
# ======================

def logout_view(request):

    logout(request)

    return redirect('login')
