import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework import status

from airport.models import AirplaneType, Airplane
from rest_framework.test import APIClient

AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")
AIRPLANE_URL = reverse("airport:airplane-list")


def sample_airplane(**params):

    defaults = {
        "name": "name",
        "rows": 10,
        "seats_in_row": 9,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)

def sample_airplane_type(**params):
    defaults = {
        "name": "Test",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)

def image_upload_url(airplane_id):
    """Return URL for recipe image upload"""
    return reverse("airport:airplane-upload-image", args=[airplane_id])


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])

class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airplane = sample_airplane()

    def tearDown(self):
        self.airplane.image.delete()
        self.airplane.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to movie"""
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airplane.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list_should_not_work(self):
        url = AIRPLANE_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "Test",
                    "rows": 10,
                    "seats_in_row": 90,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name="Test")
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.airplane.id))

        self.assertIn("image", res.data)
#
    def test_image_url_is_shown_on_airplane_list(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)

        self.assertIn("image", res.data[0].keys())


    def test_put_movie_not_allowed(self):
        payload ={
                "name": "Test",
                "rows": 10,
                "seats_in_row": 90,
        }

        airplane = sample_airplane()
        url = detail_url(airplane.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_movie_not_allowed(self):
        airplane = sample_airplane()
        url = detail_url(airplane.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
