from django.db import models
from django.contrib.auth.models import User

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    book_key = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover_id = models.IntegerField(null=True, blank=True)

    ai_summary = models.TextField(blank=True)

    ai_points = models.JSONField(
        default=list,
        blank=True
    )

    ai_targets = models.JSONField(
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    logged_in_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email or self.user.username} @ {self.logged_in_at:%Y-%m-%d %H:%M}"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query

class AIRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    input_text = models.TextField()
    result = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI - {self.user.username}"
    
from django.db import models
from django.contrib.auth.models import User

class SavedSummary(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)

    cover_url = models.URLField(blank=True)

    summary = models.TextField()

    points = models.JSONField(default=list)

    targets = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Contact(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='feedback_messages',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    admin_reply = models.TextField(blank=True)
    replied_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='feedback_replies',
        null=True,
        blank=True
    )
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} ({self.email})"

class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.otp}"