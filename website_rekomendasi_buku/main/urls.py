from django.urls import path
from .views import *

urlpatterns = [

    path('', home, name='home'),

    path('api/popular/', popular_books),
    
    path('api/search/', search_books),
    
    path('api/ai-recommendations/', ai_recommendations),

    path('ai-search/', ai_search, name='ai_search'),
    
    path('popular-books/', popular_books_page, name='popular_books_page'),

    path('favorites/', favorites, name='favorites'),

    path('contact/', contact, name='contact'),
    
    path('api/favorite/toggle/', toggle_favorite),

    path('login/', login_view, name='login'),

    path('register/', register_view, name='register'),

    path('logout/', logout_view, name='logout'),
]