from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

from math import floor

from xwtools.models import Chassis



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
