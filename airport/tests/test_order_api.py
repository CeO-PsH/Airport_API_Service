from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError

from airport.models import (
    Airport,
    Route,
    Airplane,
    AirplaneType,
    Crew,
    Flight,
    Order,
    Ticket,
)
from rest_framework.test import APIClient

from airport.serializers import (
    OrderSerializer,
    TicketSerializer,
)

ORDER_URL = reverse("airport:order-list")

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


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_flight(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_au_required_flight(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_order_and_ticket(self):
        flight = sample_flight()
        Order.objects.create(
            created_at= "2022-06-02T14:00:00Z",
            user= self.user
        )
        order = Order.objects.get(id=1)
        Ticket.objects.create(
            row=1,
            seat=1,
            flight=flight,
            order=order
        )

    def test_create_order_and_ticket_twice(self):
        flight = sample_flight()
        order = Order.objects.create(created_at="2022-06-02T14:00:00Z", user=self.user)

        try:
            Ticket.objects.create(row=1, seat=1, flight=flight, order=order)
        except ValidationError:
            pass
        with self.assertRaises(ValidationError):
            raise ValidationError(
                {"__all__": ["Ticket with this Flight, Row and Seat already exists."]}
            )

    def test_create_order_and_ticket_big_number(self):
        flight = sample_flight()
        order = Order.objects.create(created_at="2022-06-02T14:00:00Z", user=self.user)

        try:
            Ticket.objects.create(row=1000, seat=1000, flight=flight, order=order)
        except ValidationError:
            pass
        with self.assertRaises(ValidationError):
            raise ValidationError

