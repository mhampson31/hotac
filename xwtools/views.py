from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from .models import Faction, Chassis, Slot, Dial
from .serializers import FactionSerializer


def ship_sheet(request, chassis_slug):
    context = {'ship':Chassis.objects.get(slug=chassis_slug)}
    return render(request, 'campaign/chassis.html', context)

class FactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = Faction.objects.all()
    serializer_class = FactionSerializer