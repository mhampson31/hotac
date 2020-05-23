from django.db import models
from django.db.models import Sum

from xwtools.models import Chassis, Upgrade
from .campaigns import User, Campaign, Squadron


class Pilot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    callsign = models.CharField(max_length=30)
    upgrades = models.ManyToManyField(Upgrade)
    initiative = models.PositiveSmallIntegerField(default=2)

    PATH_CHOICES = (
        ('F', 'Force User'),
        ('A', 'Ace')
    )
    path = models.CharField(max_length=1, choices=PATH_CHOICES, default='A')

    def __str__(self):
        return '{} ({})'.format(self.callsign, self.user)

    @property
    def total_xp(self):
        xp = self.campaign.squadron_set.get(chassis=self.pilotship_set.first().chassis).start_xp + \
            (self.achievement_set.filter(event__team=False).aggregate(xp=Sum('event__xp'))['xp'] or 0)
        if self.campaign.pool_xp:
            return xp + self.campaign.xp_share * self.session_set.count()
        else:
            return xp + sum([a.xp for a in self.achievement_set.filter(event__team=True)])


class PilotShip(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE, null=True)
    initiative = models.PositiveSmallIntegerField(default=2)
    hull_upgrades = models.PositiveSmallIntegerField(default=0)
    shield_upgrades = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.pilot.callsign + "\'s " + self.chassis.name

    @property
    def slots(self):
        i = self.initiative if self.pilot.campaign.ship_initiative else self.pilot.initiative
        slot_list = [s.get_type_display() for s in self.chassis.slots.all()]
        path_slot = {'A':'Pilot', 'F':'Force Power'}[self.pilot.path]

        if i >= 3:
            slot_list.append(path_slot)
        if i >= 4:
            slot_list.append('Modification')
        if i >= 5:
            prog = self.pilot.campaign.squadron_set.get(id=self.chassis.id).progression
            slot_list.append({'d':path_slot,
                              'h':'Sensor'}[prog])
        if i == 6:
            slot_list.extend((path_slot, 'Modification'))
        slot_list.sort()
        return slot_list
