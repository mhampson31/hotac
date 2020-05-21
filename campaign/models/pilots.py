from django.db import models

from xwtools.models import Ship, Upgrade
from .campaigns import User, Campaign, CampaignShip


class Pilot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    callsign = models.CharField(max_length=30)
    total_xp = models.PositiveSmallIntegerField()
    upgrades = models.ManyToManyField(Upgrade)
    initiative = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return '{} ({})'.format(self.callsign, self.user)


class PilotShip(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    ship = models.ForeignKey(CampaignShip, on_delete=models.CASCADE, null=True)
    initiative = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return self.pilot.callsign + "\'s " + self.ship.name

    @property
    def slots(self):
        i = [self.initiative if self.pilot.campaign.ship_initiative else self.pilot.initiative]
        return self.ship.slots.filter(initiative__lte=i)
