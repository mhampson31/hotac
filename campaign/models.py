from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

import re
from math import floor
from random import choice

from mptt.models import MPTTModel, TreeForeignKey
from smart_selects.db_fields import ChainedForeignKey

UPGRADE_TYPES = {
    'Astromech':'AST',
    'Cannon': 'CNN',
    'Configuration': 'CNF',
    'Crew': 'CRW',
    'Device': 'DVC',
    'Force Power': 'FRC',
    'Gunner': 'GNR',
    'Illicit': 'ILC',
    'Missile': 'MSL',
    'Modification': 'MOD',
    'Sensor':'SNS',
    'Tactical Relay': 'TAC',
    'Talent': 'TLN',
    'Tech': 'TCH',
    'Title': 'TTL',
    'Torpedo':'TRP',
    'Turret':'TRT',
    'Ship':'SHP',
    'Pilot':'PLT',
    'Initiative':'THR',
    'Force Charge':'FCH',
    'Charge':'CHR',
    'Wildcard':'WLD'
}
UPGRADE_CHOICES = [(v, k) for k, v in UPGRADE_TYPES.items()]



class User(AbstractUser):
    pass


class Campaign(models.Model):
    description = models.CharField(max_length=30)
    victory = models.PositiveSmallIntegerField()
    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('campaign', kwargs={'pk': self.pk})


class Dial(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class DialManeuver(models.Model):
    dial = models.ForeignKey(Dial, on_delete=models.CASCADE)
    speed = models.PositiveSmallIntegerField()

    MOVE_TYPES = {
        'Straight': 'S',
        'Bank': 'B',
        'Turn': 'T',
        'K-Turn': 'KT',
        'Tallon Roll': 'TR',
        'Sloop': 'SL',
        'Reverse Bank': 'RB',
        'Stationary': 'SS'
    }
    MOVE_CHOICES = [(v, k) for k, v in MOVE_TYPES.items()]
    move = models.CharField(max_length=3, choices=MOVE_CHOICES)

    BEARING_CHOICES = (
        ('L', 'Left'),
        ('R', 'Right')
    )
    bearing = models.CharField(max_length=1, choices=BEARING_CHOICES, null=True, blank=True )

    COLOR_CHOICES = (
        ('B', 'Blue'),
        ('W', 'White'),
        ('R', 'Red')
    )
    color = models.CharField(max_length=1, choices=COLOR_CHOICES, default='W')

    def find_mirror(self):
        if not self.bearing:
            return self
        else:
            new_bearing = {'L':'R', 'R':'L'}[self.bearing]
            return self.dial.dialmaneuver_set.get(speed=self.speed, move=self.move, bearing=new_bearing)

    @property
    def css_name(self):
        if self.bearing:
            return '{} {}'.format(self.get_move_display(), self.get_bearing_display())
        else:
            return self.get_move_display()

    @property
    def icon_color(self):
        return {'B':'easy', 'R':'hard', 'W':''}[self.color]

    def __str__(self):
        return '{} {}{}{}'.format(self.speed,
                                   self.get_move_display(),
                                   ' ' + self.get_bearing_display() if self.bearing else '',
                                   '' if self.color == 'W' else ' ' + self.get_color_display())

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('dial', 'speed', 'move', 'bearing'), name='dial_maneuver'),
        ]

class Ship(models.Model):
    name = models.CharField(max_length=20)
    start_xp = models.PositiveSmallIntegerField(default=0)
    playable = models.BooleanField(default=True)
    #css_name = models.CharField(max_length=20)
    dial = models.ForeignKey(Dial, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def css_name(self):
        return re.sub(r'[^\w\d]', '', self.name.lower())


class Upgrade(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    type2 = models.CharField(max_length=3, choices=UPGRADE_CHOICES, null=True, blank=True, default=None)
    cost = models.PositiveSmallIntegerField()
    charges = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['type', '-type2', 'name']


class Pilot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    callsign = models.CharField(max_length=30)
    total_xp = models.PositiveSmallIntegerField()
    upgrades = models.ManyToManyField(Upgrade)

    def __str__(self):
        return '{} ({})'.format(self.callsign, self.user)


class Event(models.Model):
    short_desc = models.CharField(max_length=25)
    long_desc = models.CharField(max_length=60)
    xp = models.SmallIntegerField()
    team = models.BooleanField(default=True)

    def __str__(self):
        return self.short_desc


class Mission(models.Model):
    FRIENDLY = 'F'
    NEUTRAL = 'N'
    HOSTILE = 'H'
    TERRITORY_CHOICES = (
        (FRIENDLY, 'Friendly'),
        (NEUTRAL, 'Neutral'),
        (HOSTILE, 'Hostile')
    )
    name = models.CharField(max_length=30)
    story = models.CharField(max_length=30)
    sequence = models.PositiveSmallIntegerField()
    territory = models.CharField(max_length=1, choices=TERRITORY_CHOICES)

    def __str__(self):
        return '{} ({} {})'.format(self.name, self.story, self.sequence)


class Session(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    pilots = models.ManyToManyField(Pilot)
    date = models.DateField()
    VICTORY = 'V'
    FAILURE = 'F'
    UNRESOLVED = 'U'
    OUTCOME_CHOICES = (
        (VICTORY, 'Victory'),
        (FAILURE, 'Failure'),
        (UNRESOLVED, 'Unresolved')
    )
    outcome = models.CharField(max_length=1, choices=OUTCOME_CHOICES, default='U')

    def __str__(self):
        return '{} {}'.format(self.mission.name, self.date)

    @property
    def xp_total(self):
        a = self.achievement_set.filter(event__team=True)
        return a.aggregate(total=(models.Sum('threat') or 0) + (models.Sum('event__xp') or 0))['total'] or 0

    @property
    def xp_earned(self):
        return floor(self.xp_total/self.pilots.count())

    @property
    def xp_remainder(self):
        return self.xp_total - (self.pilots.count() * self.xp_earned)


class Achievement(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, default=1)
    turn = models.PositiveSmallIntegerField()
    threat = models.SmallIntegerField(null=True, blank=True)


class Slot(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    threat = models.PositiveSmallIntegerField()
    cost = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)


class TreeSlot(MPTTModel):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    threat = models.PositiveSmallIntegerField()
    cost = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    type2 = models.CharField(max_length=3, choices=UPGRADE_CHOICES, null=True, blank=True, default=None)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return '{} {} - {} [{}]'.format(self.ship.name, self.threat, self.get_type_display(), self.cost)

    class Meta:
        ordering = ['threat', 'id', 'cost']


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


class AI(models.Model):
    dial = models.ForeignKey(Dial, on_delete=models.CASCADE)
    flee = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return '{} AI'.format(self.dial.name)

    def mirror(self):
        """
        A helper function that makes left-sided copies of all the right-side maneuver tables
        :return: Nothing, saves new objects directly
        """

        for mv in self.aimaneuver_set.filter(direction__in=('FR', 'RF', 'RA', 'AR')):
            new_dir = mv.direction.replace('R', 'L')
            if not self.aimaneuver_set.filter(direction=new_dir, range=mv.range).exists():
                mv.pk = None
                mv.direction = new_dir
                mv.roll_1 = mv.roll_1.find_mirror()
                mv.roll_2 = mv.roll_2.find_mirror()
                mv.roll_3 = mv.roll_3.find_mirror()
                mv.roll_4 = mv.roll_4.find_mirror()
                mv.roll_5 = mv.roll_5.find_mirror()
                mv.roll_6 = mv.roll_6.find_mirror()
                mv.save()


class AIManeuver(models.Model):
    RANGE_CHOICES = (
        ('1', 'R1/R2 Closing'),
        ('2', 'R3/R2 Fleeing'),
        ('3', 'R4+'),
        ('4', 'Stressed')
    )
    AI_ARC_TYPES = {
        'Bullseye': 'BE',
        'Forward (Right)': 'FR',
        'Right (Forward)': 'RF',
        'Right (Aft)': 'RA',
        'Aft (Right)': 'AR',
        'Forward (Left)': 'FL',
        'Left (Forward)': 'LF',
        'Left (Aft)': 'LA',
        'Aft (Left)': 'AL'

    }
    AI_ARC_CHOICES = [(v, k) for k, v in AI_ARC_TYPES.items()]

    ai = models.ForeignKey(AI, on_delete=models.CASCADE)
    direction = models.CharField(max_length=2, choices=AI_ARC_CHOICES)
    range = models.CharField(max_length=1, choices=RANGE_CHOICES)

    roll_1 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_1')
    roll_2 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_2')
    roll_3 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_3')
    roll_4 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_4')
    roll_5 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_5')
    roll_6 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_6')

    def get_maneuvers(self): return True

    def roll(self):
        return choice([self.roll_1, self.roll_2, self.roll_3, self.roll_4, self.roll_5, self.roll_6])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('ai', 'direction', 'range'), name='ai_maneuver'),
        ]
