from django.shortcuts import render


from .models import Ship, Slot, Dial


def ship_sheet(request, ship_slug):
    ship = Ship.objects.get(slug=ship_slug)

    context = {'ship':ship}

    return render(request, 'campaign/ship.html', context)
