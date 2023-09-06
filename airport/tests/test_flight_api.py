from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework import status

from airport.models import (
    Airport,
    Route,
    Airplane,
    AirplaneType,
    Crew,
    Flight,
)
from rest_framework.test import APIClient

from airport.serializers import (
    FlightListSerializer,
    FlightDetailSerializer,
)

FLIGHT_URL = reverse("airport:flight-list")

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

def sample_airplane_type(**params):
    defaults = {
        "name": "Test",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)

def sample_airplane(**params):

    defaults = {
        "name": "name",
        "rows": 10,
        "seats_in_row": 9,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)

def sample_flight(**params):
    route = sample_route()
    airplane = sample_airplane()
    departure_time = "2022-06-02T14:00:00Z"
    arrival_time = "2022-06-02T21:00:00Z"
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": departure_time,
        "arrival_time": arrival_time
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


def detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])

class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_flight(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_flight(self):
        sample_flight()

        res = self.client.get(FLIGHT_URL)

        flight = {
            "route": "route_start - route_end",
            "airplane_name": "name",
            "departure_time": "2022-06-02T14:00:00Z",
            "arrival_time": "2022-06-02T21:00:00Z",
            "airplane_capacity": 90,
            "tickets_available": 90,
        }

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for field in flight:
            self.assertEqual(
                res.data[0][field], flight[field])

    def test_retrieve_flight_detail(self):
        flight = sample_flight()

        url = detail_url(flight.id)
        res = self.client.get(url)

        serializer = FlightDetailSerializer(flight)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        route = sample_route()
        airplane = sample_airplane()
        payload = {
            "route": route,
            "airplane": airplane,
            "departure_time": "2022-06-02T14:00:00Z",
            "arrival_time": "2022-06-02T21:00:00Z",
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        airplane = sample_airplane()
        route = sample_route()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2022-06-02T14:00:00Z",
            "arrival_time": "2022-06-02T21:00:00Z",
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        flight = Flight.objects.get(id=res.data["id"])
        self.assertEqual(flight.route, route)


    def test_create_flight_without_route(self):
        airplane = sample_airplane()

        payload = {
            "airplane": airplane.id,
            "departure_time": "2022-06-02T14:00:00Z",
            "arrival_time": "2022-06-02T21:00:00Z",
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_flight_without_airplane(self):
        route = sample_route()
        payload = {
            "route": route.id,
            "departure_time": "2022-06-02T14:00:00Z",
            "arrival_time": "2022-06-02T21:00:00Z",
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_crew(self):
        airplane = sample_airplane()
        route = sample_route()
        crew = Crew.objects.create(first_name="Test", last_name="Test2")
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2022-06-02T14:00:00Z",
            "arrival_time": "2022-06-02T21:00:00Z",
            "crew": crew.id
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        flight = Flight.objects.get(id=res.data["id"])
        self.assertEqual(flight.route, route)

    def test_create_flight_without_date(self):
        airplane = sample_airplane()
        route = sample_route()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_filter_flight_by_id_route(self):

        city3 = sample_airport(name="route_middle")

        route = sample_route()
        route1 = sample_route(destination=city3)


        flight1 = sample_flight(route=route)
        flight2 = sample_flight(route=route1)

        res = self.client.get(FLIGHT_URL, {"route": 1})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)


        for field in serializer1.data:
            self.assertEqual(
                res.data[0][field], serializer1[field].value)

        for field in serializer2.data:
            self.assertNotIn(
                 serializer2[field].value, res.data[0])


    def test_filter_flight_by_departure_time(self):

        flight1 = sample_flight(departure_time= "2022-06-02T14:00:00Z")
        flight2 = sample_flight(departure_time= "2022-06-02T14:00:00Z")

        res = self.client.get(FLIGHT_URL, {"departure_time": "2022-06-02"})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)


        for field in serializer1.data:
            self.assertEqual(
                res.data[0][field], serializer1[field].value)

        for field in serializer2.data:
            self.assertNotIn(
                 serializer2[field].value, res.data[0])

    def test_retrieve_flight(self):
        sample_flight()

        response = self.client.get(f"{FLIGHT_URL}1/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_flight(self):
        sample_flight()
        airplane = sample_airplane()
        route = sample_route()
        data = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-06-02T14:00:00Z",
            "arrival_time": "2023-06-02T21:00:00Z",
        }
        response = self.client.put(f"{FLIGHT_URL}1/", data=data)
        self.assertEqual(response.data["departure_time"], "2023-06-02T14:00:00Z")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_flight(self):
        sample_flight()
        flight = Flight.objects.filter(id=1)
        self.assertEqual(flight.count(), 1)
        response = self.client.delete(f"{FLIGHT_URL}1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invalid_route(self):
        response = self.client.get("/api/airport/flight/1001/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)