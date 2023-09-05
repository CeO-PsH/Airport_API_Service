import uuid

from django.db import models
from rest_framework.exceptions import ValidationError
import os
from Aiport_API_Service import settings
from django.utils.text import slugify

class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

def airplane_image_file_path(instance, filename):
    _, ext = os.path.splitext(filename)

    filename = f"{slugify(instance.name)}-{uuid.uuid4()}.{ext}"
    return os.path.join("upload/airplane", filename)


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey("AirplaneType", on_delete=models.CASCADE, related_name="airplanes")
    image = models.ImageField(null=True, upload_to=airplane_image_file_path)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name

class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_cite = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Route(models.Model):
    source = models.ForeignKey("Airport", on_delete=models.CASCADE, related_name="source_routes")
    destination = models.ForeignKey("Airport", on_delete=models.CASCADE, related_name="destination_routes")
    distance = models.IntegerField()

    def __str__(self):
        return str(f"{self.source.name} - {self.destination.name}")

class Flight(models.Model):
    route = models.ForeignKey("Route",  on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey("Airplane",  on_delete=models.CASCADE, related_name="flights")
    departure_time = models.DateTimeField(auto_now_add=False)
    arrival_time = models.DateTimeField(auto_now_add=False)
    crew = models.ManyToManyField(Crew, blank=True)

    def __str__(self):
        return f"{self.route.source} - {self.route.destination}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey("Flight",  on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="tickets", default=None
    )
    def __str__(self):
        return f"Number: {self.flight}, row: {self.row}, seat: {self.seat}"

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]