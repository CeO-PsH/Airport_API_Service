import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework import status

from airport.models import AirplaneType, Airplane
from rest_framework.test import APIClient

from airport.serializers import AirplaneListSerializer, AirplaneDetailSerializer
AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")
AIRPLANE_URL = reverse("airport:airplane-list")
FLIGHT_SESSION_URL = reverse("airport:flight-list")


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


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def tearDown(self):
        Airplane.objects.all().delete()

    def test_list_airplane(self):
        v = list(Airplane.objects.all())
        sample_airplane()
        b = list(Airplane.objects.all())
        res = self.client.get(AIRPLANE_URL)

        airplane = Airplane.objects.order_by("id")
        serializer = AirplaneListSerializer(airplane, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_airplane_by_type(self):
        airplane_type1 = AirplaneType.objects.create(name="TestOne")
        airplane_type2 = AirplaneType.objects.create(name="TestTwo")
        airplane1 = Airplane.objects.create(
            name="Boing", rows=5, seats_in_row=5, airplane_type=airplane_type1
        )
        airplane2 = Airplane.objects.create(
            name="Mria", rows=5, seats_in_row=5, airplane_type=airplane_type2
        )
        airplane3 = Airplane.objects.create(
            name="test", rows=5, seats_in_row=5,
        )

        res = self.client.get(
            AIRPLANE_URL, {"airplane_type": f"{airplane_type1.id},{airplane_type2.id}"}
        )

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)
        serializer3 = AirplaneListSerializer(airplane3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_airplane_by_name(self):

        airplane1 = Airplane.objects.create(
            name="Boing", rows=5, seats_in_row=5
        )
        airplane2 = Airplane.objects.create(
            name="Mria", rows=5, seats_in_row=5
        )
        airplane3 = Airplane.objects.create(
            name="test", rows=5, seats_in_row=5,
        )

        res = self.client.get(
            AIRPLANE_URL, {"name": "Mria"}
        )

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)
        serializer3 = AirplaneListSerializer(airplane3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_airplane_detail(self):
        airplane = sample_airplane()

        url = detail_url(airplane.id)
        res = self.client.get(url)

        serializer = AirplaneDetailSerializer(airplane)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "Test",
            "rows": 10,
            "seats_in_row": 9,
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        payload = {
            "name": "Test",
            "rows": 10,
            "seats_in_row": 9,
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(airplane, key))

    def test_create_airplane_with_type(self):
        airplane_type_1 = AirplaneType.objects.create(name="test")
        payload = {
            "name": "Test",
            "rows": 10,
            "seats_in_row": 9,
            "airplane_type": airplane_type_1.id
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        airplane = Airplane.objects.get(id=res.data["id"])
        airplane_type = airplane.airplane_type
        self.assertEqual(airplane_type.name, "test")

