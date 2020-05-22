from django.db import models

from xwtools.models import Chassis, Upgrade
from .campaigns import User, Campaign, Squadron


class Pilot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    callsign = models.CharField(max_length=30)
    total_xp = models.PositiveSmallIntegerField()
    upgrades = models.ManyToManyField(Upgrade)
    initiative = models.PositiveSmallIntegerField(default=2)

    SLOT_CHOICES = (
        ('FRC', 'Force'),
        ('TLN', 'Talent')
    )
    init_3 = models.CharField(max_length=3, choices=SLOT_CHOICES, default='TLN')
    init_5 = models.CharField(max_length=3, choices=SLOT_CHOICES, default='TLN')
    init_6 = models.CharField(max_length=3, choices=SLOT_CHOICES, default='TLN')

    def __str__(self):
        return '{} ({})'.format(self.callsign, self.user)


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

        if i >= 3:
            slot_list.append(self.pilot.get_init_3_display())
        if i >= 4:
            slot_list.append('Modification')
        if i >= 5:
            prog = self.pilot.campaign.squadron_set.get(id=self.chassis.id).progression
            slot_list.append({'d':self.pilot.get_init_5_display(),
                              'h':'Sensor'}[prog])
        if i == 6:
            slot_list.extend((self.pilot.get_init_6_display(), 'Modification'))
        slot_list.sort()
        return slot_list
