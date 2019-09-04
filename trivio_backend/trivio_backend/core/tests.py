from django.test import TestCase
from django.urls import resolve

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from trivio_backend.core import models
from trivio_backend.core.external import verify_email
from trivio_backend.core.views.auth import enrich_user


class PostsApiTestCase(TestCase):
    def setUp(self):
        self.user = models.User.objects.create(
            email="me@example.com",
            username="me",
            password="qwerty"
        )
        self.user2 = models.User.objects.create(
            email="me2@example.com",
            username="me2",
            password="qwerty"
        )
        self.factory = APIRequestFactory()

    def _post_api(self, url, data=None, user=None):
        if user is None:
            user = self.user
        request = self.factory.post(url, data, format="json")
        force_authenticate(request, user=user)
        match = resolve(url)
        return match.func(request, *match.args, **match.kwargs)

    def _get_api(self, url, data=None, user=None):
        if user is None:
            user = self.user
        request = self.factory.get(url, data, format="json")
        force_authenticate(request, user=user)
        match = resolve(url)
        return match.func(request, *match.args, **match.kwargs)

    def test_userCreatesPost(self):
        post = self._post_api("/api/v1/posts/", {
            "content": "post content",
            "title": "title"
        }).data
        self.assertEqual(post["title"], "title")
        self.assertEqual(models.Post.objects.count(), 1)

    def test_userLikingActivity(self):
        post = models.Post.objects.create(
            user=self.user2,
            content="content",
            title="title"
        )
        # first like
        self._post_api(f"/api/v1/posts/{post.id}/like/")
        self.assertEqual(post.likes.count(), 1)

        # second like
        self._post_api(f"/api/v1/posts/{post.id}/like/")
        self.assertEqual(post.likes.count(), 1)

        # unlike
        self._post_api(f"/api/v1/posts/{post.id}/unlike/")
        self.assertEqual(post.likes.count(), 0)

        # second unlike
        self._post_api(f"/api/v1/posts/{post.id}/unlike/")
        self.assertEqual(post.likes.count(), 0)

    def test_multiUserLike(self):
        post = models.Post.objects.create(
            user=self.user,
            content="content",
            title="title"
        )
        user3 = models.User.objects.create(
            email="me3@example.com",
            username="me3",
            password="qwerty"
        )
        self._post_api(f"/api/v1/posts/{post.id}/like/", user=self.user2)
        self._post_api(f"/api/v1/posts/{post.id}/like/", user=user3)

        self.assertEqual(post.likes.count(), 2)

    def test_selfLiking(self):
        post = models.Post.objects.create(
            user=self.user,
            content="content",
            title="title"
        )
        response = self._post_api(f"/api/v1/posts/{post.id}/like/", user=self.user)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_getPost(self):
        response = self._get_api(f"/api/v1/posts/1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        post = models.Post.objects.create(
            user=self.user,
            content="content",
            title="title"
        )
        post.likes.add(self.user2)

        post_json = self._get_api(f"/api/v1/posts/{post.id}/").data
        self.assertEqual(post.id, post_json["id"])
        self.assertEqual(post_json["num_likes"], 1)
        self.assertEqual(post_json["title"], "title")


class Patches:
    @staticmethod
    def call_external_api_none(*args, **kwargs):
        return None

    @staticmethod
    def call_external_api_hunter(*args, **kwargs):
        return {
            "data": {
                "regexp": True,
                "smtp_server": True,
                "smtp_check": True
            }
        }

    @staticmethod
    def call_external_api_clearbit(*args, **kwargs):
        return {
            "name": {
                "givenName": "first_name",
                "familyName": "last_name",
            },
            "location": "Moscow"
        }


class ExternalTestCase(TestCase):
    @patch("trivio_backend.core.external.call_external_api", Patches.call_external_api_hunter)
    @patch("django.conf.settings.EMAIL_HUNTER_API_KEY", "123")
    def test_verifyEmail(self):
        self.assertFalse(verify_email("sadqewqew"))
        self.assertFalse(verify_email("a@b_.c"))
        self.assertTrue(verify_email("diver@gmail.com"))

    @patch("trivio_backend.core.external.call_external_api", Patches.call_external_api_none)
    @patch("django.conf.settings.EMAIL_HUNTER_API_KEY", "123")
    def test_notVerifyEmail(self):
        self.assertFalse(verify_email("diver@gmail.com"))

    @patch("trivio_backend.core.external.call_external_api", Patches.call_external_api_clearbit)
    @patch("django.conf.settings.CLEARBIT_API_KEY", "123")
    def test_enrich_user(self):
        user = models.User.objects.create(
            email="me@example.com",
            username="me",
            password="qwerty",
            last_name="other_name"
        )
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, 'other_name')
        self.assertEqual(user.location, None)
        enrich_user(user.email, user)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "first_name")
        self.assertEqual(user.last_name, 'other_name')
        self.assertEqual(user.location, "Moscow")

    @patch("trivio_backend.core.external.call_external_api", Patches.call_external_api_none)
    @patch("django.conf.settings.CLEARBIT_API_KEY", "123")
    def test_not_enrich_user(self):
        user = models.User.objects.create(
            email="me@example.com",
            username="me",
            password="qwerty"
        )
        enrich_user(user.email, user)
        user.refresh_from_db()
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.location, None)


class AuthTestCase(TestCase):
    @patch("trivio_backend.core.views.auth.verify_email", lambda email: True)
    @patch("trivio_backend.core.views.auth.enrich_email", lambda email: {})
    def test_signup(self):
        self.assertEqual(models.User.objects.count(), 0)

        factory = APIRequestFactory()
        url = "/api/v1/auth/signup/"
        request = factory.post(url, {
            "email": "me@example.com",
            "username": "me",
            "password": "qwerty"
        }, format="json")
        match = resolve(url)
        match.func(request, *match.args, **match.kwargs)

        self.assertEqual(models.User.objects.count(), 1)
