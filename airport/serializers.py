from typing import Any

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    AirplaneType,
    Airplane,
    Crew,
    Airport,
    Route,
    Flight,
    Ticket,
    Order,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class AirportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "closest_big_cite",
            "country",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type"
        )


class AirplaneListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "image")


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity",
            "image"
        )


class AirplaneImageSerializer(AirplaneSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(
        source="destination.name",
        read_only=True
    )


class RouteDetailSerializer(RouteSerializer):
    source = AirportListSerializer(many=False, read_only=True)
    destination = AirportListSerializer(many=False, read_only=True)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane",
            "departure_time",
            "route",
            "arrival_time",
            "crew"
        )


class FlightListSerializer(FlightSerializer):
    airplane_name = serializers.CharField(
        source="airplane.name",
        read_only=True
    )
    airplane_capacity = serializers.IntegerField(
        source="airplane.capacity",
        read_only=True
    )
    route = serializers.StringRelatedField(many=False, read_only=True)

    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "airplane_name",
            "airplane_capacity",
            "route",
            "tickets_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs) -> Any:
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightDetailSerializer(FlightSerializer):
    airplane = serializers.StringRelatedField(many=False, read_only=True)
    airplane_type = serializers.CharField(
        source="airplane.airplane_type.name", read_only=True
    )

    crew = CrewSerializer(many=True, read_only=True)
    distance = serializers.IntegerField(
        source="route.distance",
        read_only=True
    )
    route_source = serializers.CharField(
        source="route.source",
        read_only=True
    )
    route_destination = serializers.CharField(
        source="route.destination", read_only=True
    )
    taken_places = TicketSeatsSerializer(
        source="tickets",
        many=True,
        read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "distance",
            "airplane",
            "airplane_type",
            "crew",
            "route_source",
            "route_destination",
            "taken_places",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_null=False)

    class Meta:
        model = Order
        fields = (
            "id",
            "tickets",
            "created_at",
        )

    def create(self, validated_data) -> Order:
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
