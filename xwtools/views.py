from django.shortcuts import render


from .models import Chassis, Slot, Dial


def ship_sheet(request, chassis_slug):
    context = {'ship':Chassis.objects.get(slug=chassis_slug)}

    return render(request, 'campaign/chassis.html', context)
