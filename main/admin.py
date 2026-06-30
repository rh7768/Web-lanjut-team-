from django.contrib import admin
from .models import Wishlist, LoginHistory, SearchHistory, AIRecommendation, Contact

admin.site.register(Wishlist)
admin.site.register(LoginHistory)
admin.site.register(SearchHistory)
admin.site.register(AIRecommendation)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'user', 'created_at', 'replied_at')
    search_fields = ('name', 'email', 'message', 'admin_reply')
    list_filter = ('created_at', 'replied_at')
    readonly_fields = ('created_at',)
