from django.db import models

from .ships import Ship, Slot
from .campaigns import User, Campaign, Upgrade


class Pilot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    callsign = models.CharField(max_length=30)
    total_xp = models.PositiveSmallIntegerField()
    upgrades = models.ManyToManyField(Upgrade)

    def __str__(self):
        return '{} ({})'.format(self.callsign, self.user)


class PilotShip(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    unlocked = models.ManyToManyField(Slot)

    def locked(self):
        return Slot.objects.filter(ship=self.ship.id).difference(self.unlocked)

    def __str__(self):
        return self.pilot.callsign + "\'s " + self.ship.name

    @property
    def initiative(self):
        return len(self.unlocked.filter(type='THR')) + 1

    @property
    def threat(self):
        return self.unlocked.aggregate(t=models.Max('threat'))['t']
