from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


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


class Ship(models.Model):
    name = models.CharField(max_length=20)
    start_xp = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


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
    def xp_earned(self):
        a = self.achievement_set
        xp = a.aggregate(total=models.Sum('threat') + models.Sum('event__xp'))
        return xp['total']/self.pilots.count()


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

    def __str__(self):
        return '{} {} - {} [{}]'.format(self.ship.name, self.threat, self.get_type_display(), self.cost)

    class Meta:
        ordering = ['threat', 'id']


class PilotShip(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    unlocked = models.ManyToManyField(Slot)

    def __str__(self):
        return self.pilot.callsign + "\'s " + self.ship.name

    @property
    def initiative(self):
        return len(self.unlocked.filter(type='THR')) + 1

    @property
    def threat(self):
        return self.unlocked.aggregate(t=models.Max('threat'))['t']







TODO = """ 
players
    xp
    threat
    upgrades
missions
    enemies
    goals
ships
    name
    cost
    size
"""