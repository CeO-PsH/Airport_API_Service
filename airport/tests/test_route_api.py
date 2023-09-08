from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework import status

from airport.models import Airport, Route
from rest_framework.test import APIClient

from airport.serializers import RouteListSerializer, RouteDetailSerializer

ROUTE_URL = reverse("airport:route-list")


def sample_airport(**params):
    defaults = {
        "name": "Test",
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)

def sample_route(**params):
    source = sample_airport(name="route_start")
    destination = sample_airport(name="route_end")
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 100
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])

class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_route(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_rote(self):
        sample_route()

        res = self.client.get(ROUTE_URL)

        route = Route.objects.order_by("id")
        serializer = RouteListSerializer(route, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_route_detail(self):
        route = sample_route()

        url = detail_url(route.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        source = sample_airport(name="route_start")
        destination = sample_airport(name="route_end")
        payload = {
            "source": source,
            "destination": destination,
            "distance": 100
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        source = sample_airport(name="route_start")
        destination = sample_airport(name="route_end")
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 100
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        route = Route.objects.get(id=res.data["id"])
        self.assertEqual(payload["source"], route.source.id)

    def test_create_route_without_source(self):

        destination = sample_airport(name="route_end")
        payload = {
            "destination": destination.id,
            "distance": 100
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_route_without_destination(self):

        source = sample_airport(name="route_start")
        payload = {
            "source": source.id,

            "distance": 100
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_airport_without_distance(self):
        source = sample_airport(name="route_start")
        destination = sample_airport(name="route_end")
        payload = {
            "source": source.id,
            "destination": destination.id,
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


    def test_retrieve_roure(self):
        sample_airport()

        response = self.client.get(f"{ROUTE_URL}1/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_route(self):
        sample_airport()

        response = self.client.put(f"{Route}1/", {})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_route(self):
        sample_airport()

        response = self.client.delete(f"{Route}1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_invalid_route(self):
        response = self.client.get("/api/airport/route/1001/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)