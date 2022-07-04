from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from .models import Faction, Chassis, Slot, Dial
from .serializers import FactionSerializer, ChassisSerializer


def ship_sheet(request, chassis_slug):
    context = {'ship':Chassis.objects.get(slug=chassis_slug)}
    return render(request, 'campaign/chassis.html', context)


class FactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Faction.objects.all()
    serializer_class = FactionSerializer


class ChassisViewSet(viewsets.ModelViewSet):
    queryset = Chassis.objects.all()
    serializer_class = ChassisSerializer