from django.contrib.auth.models import User
from django.core import mail
from django.db import IntegrityError
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from .models import LoginHistory


class AuthenticationTests(TestCase):
    def test_registered_user_is_active_and_can_login_by_default(self):
        response = self.client.post(reverse('register'), {
            'username': 'pembaca',
            'email': 'pembaca@example.com',
            'password': 'rahasia123',
        })

        user = User.objects.get(username='pembaca')
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password('rahasia123'))

        response = self.client.post(reverse('login'), {
            'username': 'pembaca',
            'password': 'rahasia123',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(LoginHistory.objects.filter(user=user).exists())

    def test_invalid_login_displays_error(self):
        response = self.client.post(reverse('login'), {
            'username': 'tidak-ada',
            'password': 'salah',
        })

        self.assertContains(response, 'Username atau password salah.')

    def test_duplicate_username_displays_validation_error(self):
        User.objects.create_user(
            username='Alip',
            email='lama@example.com',
            password='rahasia123',
        )

        response = self.client.post(reverse('register'), {
            'username': 'alip',
            'email': 'baru@example.com',
            'password': 'rahasia123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username sudah digunakan.')
        self.assertContains(response, 'value="alip"')
        self.assertEqual(User.objects.filter(username__iexact='alip').count(), 1)

    @patch('main.views.User.objects.create_user')
    def test_database_duplicate_error_is_handled(self, create_user):
        create_user.side_effect = IntegrityError('duplicate username')

        response = self.client.post(reverse('register'), {
            'username': 'alip',
            'email': 'alip@example.com',
            'password': 'rahasia123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Username sudah digunakan. Silakan pilih username lain.',
        )

    @override_settings(
        REQUIRE_EMAIL_VERIFICATION=True,
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    )
    def test_manual_registration_redirects_to_login_when_verification_is_enabled(self):
        response = self.client.post(reverse('register'), {
            'username': 'verifikasi',
            'email': 'verifikasi@example.com',
            'password1': 'rahasia123',
            'password2': 'rahasia123',
        })

        user = User.objects.get(username='verifikasi')
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(user.is_active)
        self.assertEqual(len(mail.outbox), 0)


class FeedbackVisibilityTests(TestCase):
    def test_feedback_page_and_navbar_remain_available_for_regular_user(self):
        user = User.objects.create_user(
            username='pembaca',
            password='rahasia123',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('contact'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("contact")}"')

    def test_feedback_page_and_navbar_are_hidden_from_admin(self):
        admin = User.objects.create_user(
            username='admin',
            password='rahasia123',
            is_staff=True,
        )
        self.client.force_login(admin)

        response = self.client.get(reverse('contact'))
        self.assertRedirects(response, reverse('message_list'))

        response = self.client.get(reverse('home'))
        self.assertNotContains(response, f'href="{reverse("contact")}"')
