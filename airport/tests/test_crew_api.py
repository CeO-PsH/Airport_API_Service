from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework import status

from airport.models import Crew
from rest_framework.test import APIClient

from airport.serializers import CrewSerializer

CREW_TYPE_URL = reverse("airport:crew-list")


def sample_crew(**params):
    defaults = {
        "first_name": "Test",
        "last_name": "Last_Test",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_crew(self):
        res = self.client.get(CREW_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_crew(self):
        sample_crew()

        res = self.client.get(CREW_TYPE_URL)

        crew = Crew.objects.order_by("id")
        serializer = CrewSerializer(crew, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_crew_forbidden(self):
        payload = {
        "first_name": "Test",
        "last_name": "Last_Test",
        }
        res = self.client.post(CREW_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class AdminCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        payload = {
        "first_name": "Test",
        "last_name": "Last_Test",
        }

        res = self.client.post(CREW_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane_type = Crew.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(airplane_type, key))

    def test_retrieve_crew(self):
        sample_crew()

        response = self.client.get(f"{CREW_TYPE_URL}1/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_crew(self):
        sample_crew()

        response = self.client.put(f"{CREW_TYPE_URL}1/", {})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_crew(self):
        sample_crew()

        response = self.client.delete(f"{CREW_TYPE_URL}1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_invalid_crew(self):
        response = self.client.get("/api/airport/crew/1001/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)