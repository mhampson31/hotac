from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

from xwtools.models import Ship


class User(AbstractUser):
    pass


class Campaign(models.Model):
    description = models.CharField(max_length=30)
    victory = models.PositiveSmallIntegerField()
    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ships = models.ManyToManyField(Ship, through='CampaignShip')

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('campaign', kwargs={'pk': self.pk})


class CampaignShip(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    start_xp = models.PositiveSmallIntegerField(default=0)
    playable = models.BooleanField(default=True)

    @property
    def name(self):
        return self.ship.name

    def __str__(self):
        return self.name


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
