from rest_framework import serializers

from .models import Faction, Chassis


class FactionSerializer(serializers.ModelSerializer):
    ships = serializers.StringRelatedField(many=True)
    default_ship = serializers.StringRelatedField()

    class Meta:
        model = Faction
        fields = ['name', 'ships', 'default_ship']


class ChassisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chassis
        fields = ['name', 'slug', 'size', 'attack', 'attack_arc',
                  'attack2', 'attack2_arc', 'agility', 'hull', 'shields',
                  'energy', 'hyperdrive', 'walker', 'armor', 'css', 'ability']


