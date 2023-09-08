from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework import status

from airport.models import AirplaneType
from rest_framework.test import APIClient

from airport.serializers import AirplaneTypeSerializer

AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")


def sample_airplane_type(**params):
    defaults = {
        "name": "Test",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)

def detail_url(airplane_type_id):
    return reverse("airport:airplanetype-detail", args=[airplane_type_id])


class UnauthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_airplane_type(self):
        sample_airplane_type()


        res = self.client.get(AIRPLANE_TYPE_URL)

        airplane_type = AirplaneType.objects.order_by("id")
        serializer = AirplaneTypeSerializer(airplane_type, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_type_forbidden(self):
        payload = {
            "name": "test",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class AdminAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_type(self):
        payload = {
            "name": "test1",
        }

        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane_type = AirplaneType.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(airplane_type, key))

    def test_retrieve_airplane_type(self):
        sample_airplane_type()

        response = self.client.get(f"{AIRPLANE_TYPE_URL}1/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_airplane_type(self):
        sample_airplane_type()

        response = self.client.put(f"{AIRPLANE_TYPE_URL}1/", {})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_airplane_type(self):
        sample_airplane_type()

        response = self.client.delete(f"{AIRPLANE_TYPE_URL}1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_invalid_airplane_type(self):
        response = self.client.get("/api/airport/airplane_type/1001/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)