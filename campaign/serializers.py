from rest_framework import serializers
from .models import User, Pilot, PilotShip

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class PilotSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    campaign = serializers.StringRelatedField()


    class Meta:
        model = Pilot
        fields = ['user', 'campaign', 'ships', 'callsign', 'initiative', 'bonus_xp']

class PilotShipSerializer(serializers.ModelSerializer):
    pilot = PilotSerializer()
    chassis = serializers.StringRelatedField(many=True)

    class Meta:
        model = PilotShip
        fields = ['pilot', 'chassis', 'active', 'name']
