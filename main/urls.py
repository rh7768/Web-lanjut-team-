from django.urls import path
from .views import *

urlpatterns = [

    path('', home, name='home'),

    path('api/popular/', popular_books),
    
    path('api/search/', search_books),

    path('api/book-detail/', book_detail),

    path('ringkasan-ai/', ringkasan_ai, name='ringkasan_ai'),
    
    path('popular-books/', popular_books_page, name='popular_books_page'),

    path('favorites/', favorites, name='favorites'),

    path('contact/', contact, name='contact'),
    path('messages/', message_list, name='message_list'),
    path('messages/<int:contact_id>/reply/', reply_message, name='reply_message'),
    path('messages/<int:contact_id>/delete/', delete_message, name='delete_message'),

    path('about/', about, name='about'),
    
    path('api/favorite/toggle/', toggle_favorite),

    path('login/', login_view, name='login'),

    path('register/', register_view, name='register'),
    path('verify-otp/', verify_otp, name='verify_otp'),

    path('logout/', logout_view, name='logout'),
]
