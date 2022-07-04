from rest_framework import serializers

from .models import Faction


class FactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faction
        fields = ['name', 'ships', 'default_ship']

