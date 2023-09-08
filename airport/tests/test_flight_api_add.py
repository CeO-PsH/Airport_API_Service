from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase, override_settings
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


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_flight(self):
        sample_flight()

        response = self.client.get(f"{FLIGHT_URL}11/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_delete_flight(self):
        sample_flight()
        flight = Flight.objects.filter(id=7)
        self.assertEqual(flight.count(), 1)
        response = self.client.delete(f"{FLIGHT_URL}7/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        Flight.objects.all().delete()

    def test_put_flight(self):
        w = sample_flight()
        airplane = sample_airplane()
        route = sample_route()
        data = {
            "id": 10,
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-06-02T14:00:00Z",
            "arrival_time": "2023-06-02T21:00:00Z",
        }
        response = self.client.put(f"{FLIGHT_URL}10/", data=data)
        self.assertEqual(response.data["departure_time"], "2023-06-02T14:00:00Z")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_flight_by_id_route(self):

        city3 = sample_airport(name="route_middle")

        route = sample_route()
        route1 = sample_route(destination=city3)


        flight1 = sample_flight(route=route)
        flight2 = sample_flight(route=route1)

        res = self.client.get(FLIGHT_URL, {"route": 11})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)


        for field in serializer1.data:
            self.assertEqual(
                res.data[0][field], serializer1[field].value)

        for field in serializer2.data:
            self.assertNotIn(
                 serializer2[field].value, res.data[0])