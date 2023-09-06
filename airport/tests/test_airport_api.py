from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework import status

from airport.models import Airport
from rest_framework.test import APIClient

from airport.serializers import AirportListSerializer

AIRPORT_URL = reverse("airport:airport-list")


def sample_airport(**params):
    defaults = {
        "name": "Test",
        "closest_big_cite": "Rivne",
        "country": "Ukraine"
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_airport(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_airport(self):
        sample_airport()


        res = self.client.get(AIRPORT_URL)

        airplane_type = Airport.objects.order_by("id")
        serializer = AirportListSerializer(airplane_type, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airport_forbidden(self):
        payload = {
            "name": "test",
            "closest_big_cite": "Rivne",
            "country": "Ukraine"
        }
        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class AdminAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airport(self):
        payload = {
            "name": "test",
            "closest_big_cite": "Rivne",
            "country": "Ukraine"
        }

        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane_type = Airport.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(airplane_type, key))

    def test_create_airport_without_country_and_closest_big_cite(self):
        payload = {
            "name": "test",
        }

        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane_type = Airport.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(airplane_type, key))

    def test_filter_airport_by_name(self):
        airport1 = sample_airport(name="Barcelona")
        airport2 = sample_airport(name="Rivne")
        airport3 = sample_airport(name="Kennedy")

        res = self.client.get(AIRPORT_URL, {"name": "Barcelona"})

        serializer1 = AirportListSerializer(airport1)
        serializer2 = AirportListSerializer(airport2)
        serializer3 = AirportListSerializer(airport3)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_airport(self):
        sample_airport()

        response = self.client.get(f"{AIRPORT_URL}1/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_airport(self):
        sample_airport()

        response = self.client.put(f"{AIRPORT_URL}1/", {})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_airport(self):
        sample_airport()

        response = self.client.delete(f"{AIRPORT_URL}1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_invalid_airplane_type(self):
        response = self.client.get("/api/airport/airport/1001/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)