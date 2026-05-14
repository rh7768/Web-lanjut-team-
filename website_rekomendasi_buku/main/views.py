import json
import requests

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Wishlist, SearchHistory, AIRecommendation, LoginHistory


# ======================
# STORAGE FAVORITE (for backward compatibility)
# ======================

favorite_books = []


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
    cover_id = None
    if cover_url and 'id/' in cover_url:
        try:
            cover_id = int(cover_url.split('id/')[1].split('-')[0])
        except:
            pass

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

        books.append({
            'key': item['book_key'],
            'title': item['title'],
            'author': item['author'],
            'year': None,
            'cover_url': cover_url,
            'language': 'English',
            'description': 'Book from OpenLibrary API',
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
                'language': 'English',
                'description': 'Book from OpenLibrary API',
                'is_favorite': is_favorite
            })

    return JsonResponse({
        'books': books,
        'total': total
    })


# ======================
# HOME
# ======================

@login_required(login_url='login')
def home(request):

    return render(request, 'home.html')


# ======================
# AI RECOMMENDATIONS
# ======================

def ai_recommendations(request):
    """
    API untuk AI Search/Recommendations
    Simpan input dan hasil ke database
    """
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)

    if not query:
        return JsonResponse({
            'books': [],
            'total': 0
        })

    # Simpan AI recommendation jika user login
    if request.user.is_authenticated:
        AIRecommendation.objects.create(
            user=request.user,
            input_text=query,
            result=f"AI Search for: {query}"
        )

    limit = 20

    # Cari berdasarkan query (bisa berbagai keyword)
    url = (
        f"https://openlibrary.org/search.json"
        f"?q={query}&page={page}&limit={limit}"
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
                'language': 'English',
                'description': 'Book from OpenLibrary API',
                'is_favorite': is_favorite
            })

    return JsonResponse({
        'books': books,
        'total': total
    })


# ======================
# AI SEARCH
# ======================

@login_required(login_url='login')
def ai_search(request):

    return render(request, 'ai-search.html')


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
    wishlists = Wishlist.objects.filter(user=request.user)
    
    # Convert ke format yang sama dengan api response
    favorites_data = []
    for wishlist in wishlists:
        cover_url = None
        if wishlist.cover_id:
            cover_url = f"https://covers.openlibrary.org/b/id/{wishlist.cover_id}-L.jpg"
        
        favorites_data.append({
            'key': wishlist.book_key,
            'title': wishlist.title,
            'author': wishlist.author,
            'cover_url': cover_url,
            'language': 'English',
            'description': 'Book from OpenLibrary API'
        })

    return render(request, 'favorites.html', {
        'favorites': favorites_data
    })


# ======================
# CONTACT
# ======================

@login_required(login_url='login')
def contact(request):

    return render(request, 'contact.html')


# ======================
# LOGIN
# ======================

def login_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

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

    return render(request, 'auth/login.html')


# ======================
# REGISTER
# ======================

def register_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(request, 'auth/register.html')


# ======================
# LOGOUT
# ======================

def logout_view(request):

    logout(request)

    return redirect('login')