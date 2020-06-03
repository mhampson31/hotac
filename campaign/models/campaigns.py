from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

from smart_selects.db_fields import ChainedForeignKey

from math import floor

from xwtools.models import Chassis, Faction, SlotChoice, Upgrade


class User(AbstractUser):
    pass


class Campaign(models.Model):
    description = models.CharField(max_length=30)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ships = models.ManyToManyField(Chassis, through='PlayerShip')
    ship_cost = models.SmallIntegerField(default=5)

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


class PlayerShip(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE)
    xp_value = models.SmallIntegerField(default=    0)

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
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='events')
    short_desc = models.CharField(max_length=25)
    long_desc = models.CharField(max_length=120)
    xp = models.SmallIntegerField(default=1)
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
    enemy_faction = models.ForeignKey(Faction, on_delete=models.CASCADE, default=1)
    territory = models.CharField(max_length=1, choices=TERRITORY_CHOICES)

    def __str__(self):
        return '{} ({} {})'.format(self.name, self.story, self.sequence)



class EnemyPilot(models.Model):
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    upgrades = models.ManyToManyField(Upgrade, through='EnemyAbility')

    def __str__(self):
        if self.chassis is self.faction.default_ship:
            return self.chassis_name
        else:
            return '{} - {}'.format(self.chassis.name, self.in5)

    def ability_list(self, lvl=1):
        return '/'.join(self.abilities.filter(level__lte=lvl).values_list('upgrade__name', flat=True))

    @property
    def basic(self):
        return '/'.join(self.abilities.filter(level=1).values_list('upgrade__name', flat=True))

    @property
    def elite(self):
        return '/'.join(self.abilities.filter(level=2).values_list('upgrade__name', flat=True))

    @property
    def in3(self):
        return '/'.join(self.abilities.filter(level=3).values_list('upgrade__name', flat=True))

    @property
    def in4(self):
        return '/'.join(self.abilities.filter(level=4).values_list('upgrade__name', flat=True))

    @property
    def in5(self):
        return '/'.join(self.abilities.filter(level=5).values_list('upgrade__name', flat=True))


class EnemyAbility(models.Model):
    pilot = models.ForeignKey(EnemyPilot, on_delete=models.CASCADE, related_name='abilities')
    upgrade = models.ForeignKey(Upgrade, on_delete=models.CASCADE, limit_choices_to={'ai_description__isnull':False})

    class Level(models.IntegerChoices):
        BASIC = 1
        ELITE = 2
        IN_3 = 3
        IN_4 = 4
        IN_5 = 5

    level = models.SmallIntegerField(choices=Level.choices, default=1)



class FlightGroup(models.Model):
    name = models.CharField(max_length=20)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='flight_groups')
    arrival = models.SmallIntegerField(default=1)
    vector = models.CharField(max_length=3)

    ORDERS_CHOICES = (
        ('A', 'Attack'),
        ('S', 'Strike'),
        ('E', 'Escort'),
        ('X', 'Special')
    )
    orders = models.CharField(max_length=1, choices=ORDERS_CHOICES, default="S")

    def __str__(self):
        return self.name

    def generate(self, pilots, group_init):
        sq = self.squad_members.filter(players__lte=pilots).filter(init__lte=group_init)
        # how many default enemies do we need to replace?
        r = sq.filter(action='R').count()
        squad = []
        for s in sq:
            if r and s.is_default:
                r = r-1
                pass
            else:
                squad.append(s.generate(group_init))
        return squad


class FGSetup(models.Model):
    action = models.CharField(max_length=1, choices=( ('A', 'Add'), ('R', 'Replace') ), default='A')
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE, null=True, blank=True)
    flight_group = ChainedForeignKey(FlightGroup,
                                            chained_field='mission',
                                            chained_model_field='mission',
                                            on_delete=models.CASCADE,
                                            related_name='squad_members')
    players = models.SmallIntegerField(default=1)
    init = models.SmallIntegerField(default=1)
    elite = models.BooleanField(default=False)

    def __str__(self):
        return self.chassis.name if self.chassis else 'Random'

    @property
    def is_default(self):
        return self.chassis == self.mission.enemy_faction.default_ship

    def generate(self, group_init):
        from random import choice
        from .sessions import SessionEnemy
        enemies = EnemyPilot.objects.filter(faction=self.mission.enemy_faction)
        if not self.chassis:
            ship = choice(enemies)

            #self.mission.enemy_faction.ships.exclude(id=self.mission.enemy_faction.default_ship.id))
        else:
            ship = self.chassis

        if self.elite:
            e = choice(enemies.filter(chassis=ship.chassis, faction=self.mission.enemy_faction))
            id = e.id
            #abilities = e.ability_list(lvl=group_init)
            abilities = e.abilities.filter(level__lte=group_init)
            initiative = min(group_init+1, 6)
        else:
            id = None
            abilities = None
            initiative = 1

        return  {'ship':ship.chassis,
                'initiative':initiative,
                'elite':self.elite,
                'abilities': abilities,
                'id':id}
