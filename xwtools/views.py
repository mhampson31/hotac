from django.shortcuts import render


from .models import Chassis, Slot, Dial


def ship_sheet(request, ship_slug):
    context = {'ship':Chassis.objects.get(slug=ship_slug)}

    return render(request, 'campaign/ship.html', context)
