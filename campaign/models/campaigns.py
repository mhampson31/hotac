from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

from math import floor

from xwtools.models import Chassis, Faction, UPGRADE_CHOICES


class User(AbstractUser):
    pass


class Campaign(models.Model):
    description = models.CharField(max_length=30)
    victory = models.PositiveSmallIntegerField()
    ship_initiative = models.BooleanField(default=False)
    pool_xp = models.BooleanField(default=False)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ships = models.ManyToManyField(Chassis, through='Squadron')

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('campaign', kwargs={'pk': self.pk})

    @property
    def xp_share(self):
        pilots = 0
        xp = 0
        for s in self.session_set.all():
            pilots = pilots + s.pilots.count()
            xp = xp + s.xp_total
        return floor(xp/pilots)


class Squadron(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE)
    start_xp = models.PositiveSmallIntegerField(default=10)
    playable = models.BooleanField(default=True)

    PROGRESSION_TYPES = (
        ('d', 'Default'),
        ('h', 'HWK-290')
    )
    progression = models.CharField(max_length=1, choices=PROGRESSION_TYPES, default='d')

    @property
    def name(self):
        return self.chassis.name

    def __str__(self):
        return self.name


class Event(models.Model):
    short_desc = models.CharField(max_length=25)
    long_desc = models.CharField(max_length=120)
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


class EnemyUpgrade(models.Model):
    name = models.CharField(max_length=30)
    ability = models.CharField(max_length=240)
    type = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    charges = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class EnemyPilot(models.Model):
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    upgrades = models.ManyToManyField(EnemyUpgrade, through='EnemyAbility')

    def ability_list(self, lvl):
        return '/'.join(self.abilities.filter(level=lvl).values_list('upgrade__name', flat=True))

    @property
    def basic(self):
        return self.ability_list(1)

    @property
    def elite(self):
        return self.ability_list(2)

    @property
    def in3(self):
        return self.ability_list(3)

    @property
    def in4(self):
        return self.ability_list(4)

    @property
    def in5(self):
        return self.ability_list(5)


class EnemyAbility(models.Model):
    pilot = models.ForeignKey(EnemyPilot, on_delete=models.CASCADE, related_name='abilities')
    upgrade = models.ForeignKey(EnemyUpgrade, on_delete=models.CASCADE)

    LEVEL_CHOICES = (
        (1, 'Basic'),
        (2, 'Elite'),
        (3, 'IN 3+'),
        (4, 'IN 4+'),
        (5, 'IN 5+')
    )
    level = models.SmallIntegerField(choices=LEVEL_CHOICES, default=1)
