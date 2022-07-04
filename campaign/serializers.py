from rest_framework import serializers
from .models import User, Pilot

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class PilotSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    campaign = serializers.StringRelatedField()
    ships = serializers.StringRelatedField(many=True)
    class Meta:
        model = Pilot
        fields = ['user', 'campaign', 'ships', 'callsign', 'initiative', 'bonus_xp']