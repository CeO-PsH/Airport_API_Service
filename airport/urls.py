from django.urls import path, include
from rest_framework import routers

from airport.views import AirplaneTypeViewSet, AirplaneViewSet

router = routers.DefaultRouter()
router.register("airplane_type", AirplaneTypeViewSet)
router.register("airplane", AirplaneViewSet)

urlpatterns = [path("", include(router.urls))]

app_name= "airport"