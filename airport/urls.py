from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    AirportViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register("airplane_type", AirplaneTypeViewSet)
router.register("airplane", AirplaneViewSet)
router.register("crew", CrewViewSet)
router.register("airport", AirportViewSet)
router.register("router", RouteViewSet)
router.register("flight", FlightViewSet)
router.register("order", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
