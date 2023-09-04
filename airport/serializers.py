from rest_framework import serializers

from airport.models import AirplaneType, Airplane


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = "__all__"


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = "__all__"