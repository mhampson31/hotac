from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property

from math import floor

from xwtools.models import Chassis, Faction, SlotChoice, Card
from .enemies import EnemyPilot


class User(AbstractUser):
    pass


class UpgradeLogic(models.IntegerChoices):
    HOTAC = 1, 'HotAC'
    TEST = 2, 'Test'


class FeatureChoice(models.TextChoices):
    EMPLACEMENT = 'E', 'Emplacement'
    OBSTACLE = 'O', 'Obstacle'
    TERRAIN = 'T', 'Terrain'


class Rulebook(models.Model):
    description = models.CharField(max_length=30)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    faction = models.ForeignKey(Faction, on_delete=models.SET_NULL, null=True)
    ships = models.ManyToManyField(Chassis, through='PlayableShip')

    # player defaults
    start_init = models.PositiveSmallIntegerField(default=2)

    # configure a campaign's XP costs
    ship_cost = models.PositiveSmallIntegerField(default=5)

    upgrade_logic = models.PositiveSmallIntegerField(choices=UpgradeLogic.choices)
    initiative_progression = models.PositiveSmallIntegerField(choices=UpgradeLogic.choices)
    initiative_cost = models.PositiveSmallIntegerField(default=3)

    starter_mission = models.ForeignKey('Mission', on_delete=models.SET_NULL, null=True, related_name='starts')

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('ruleset', kwargs={'pk': self.pk})

    def get_initiative_cost(self, initiative):
        """
        Returns the XP cost of advancing to from 'iniative'-1 to 'initiative'.
        """
        if self.initiative_progression == UpgradeLogic.TEST:
            return (initiative*self.initiative_cost)^2
        elif self.initiative_progression == UpgradeLogic.HOTAC:
            return initiative * self.initiative_cost
        else:
            return 0


class PlayableShip(models.Model):
    rulebook = models.ForeignKey(Rulebook, on_delete=models.CASCADE)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE)
    xp_value = models.SmallIntegerField(default = 0)

    PROGRESSION_TYPES = (
        ('d', 'Default'),
        ('h', 'HWK-290')
    )
    progression = models.CharField(max_length=1, choices=PROGRESSION_TYPES, default='d')

    @cached_property
    def name(self):
        return self.chassis.name

    def __str__(self):
        return self.name


class MissionFeature(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=1, choices=FeatureChoice.choices)
    setup_code = models.CharField(max_length=1, blank=True)
    attack = models.PositiveSmallIntegerField(null=True, blank=True)
    attack_range = models.CharField(max_length=3, blank=True)
    hull = models.PositiveSmallIntegerField(null=True, blank=True)
    shields = models.PositiveSmallIntegerField(null=True, blank=True)
    agility = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @cached_property
    def is_emplacement(self):
        return self.type == FeatureChoice.EMPLACEMENT

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
    territory = models.CharField(max_length=1, choices=TERRITORY_CHOICES, default=NEUTRAL)
    rulebook = models.ForeignKey(Rulebook, on_delete=models.SET_NULL, null=True)
    turns = models.PositiveSmallIntegerField(default=12)

    player_vp = models.BooleanField(default=False)
    enemy_vp =  models.BooleanField(default=False)

    objective = models.TextField()
    bonus_1 = models.TextField(blank=True, null=True)
    bonus_2 = models.TextField(blank=True, null=True)
    penalty = models.TextField(blank=True, null=True)

    ground_assault = models.BooleanField(default=False)

    features = models.ManyToManyField(MissionFeature, blank=True)

    class Meta:
        ordering = ['story', 'sequence']
        indexes = [
            models.Index(fields=['story', 'sequence']),
            models.Index(fields=['rulebook']),
            models.Index(fields=['player_vp'])
        ]

    def __str__(self):
        return '{} ({} {})'.format(self.name, self.story, self.sequence)


class Campaign(models.Model):
    rulebook = models.ForeignKey(Rulebook, on_delete=models.SET_NULL, null=True)
    gm = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='campaign_gm')
    players = models.ManyToManyField(User)
    description = models.CharField(max_length=30)

    victory = models.PositiveSmallIntegerField(default=12)
    pool_xp = models.BooleanField(default=False)

    deck = models.ManyToManyField(Mission)
    deck_draw = models.JSONField(null=True)

    exclude_random = models.ManyToManyField(Chassis, blank=True)

    def __str__(self):
        return self.description

    @property
    def victory_points(self):
        return self.session_set.filter(outcome='V', player_vp=True).Count()

    @cached_property
    def xp_share(self):
        """
        Used when XP pooling is chosen for the game.
        Calculates total xp across all sessions and total number of pilot shares.
        Each mission flown earns a pilot one share in the group's total xp.
        """
        pilots = 0
        xp = 0
        for s in self.session_set.all():
            pilots = pilots + s.pilots.count()
            xp = xp + s.xp_total
        return floor(xp/pilots)

    @cached_property
    def limited_upgrades(self):
        from .pilots import PilotUpgrade
        return PilotUpgrade.objects.filter(pilot__campaign=self, card__limited=True).values_list('card__name', flat=True)

    def starting_deck(self):
        for m in Mission.objects.filter(rulebook=self.rulebook, sequence=1):
            self.deck.add(m)
        self.save()

    def draw_missions(self):
        from random import sample
        deck = list(self.deck.all())
        if self.rulebook.starter_mission in deck:
            self.deck_draw = [self.starter_mission.id,]
        elif len(deck) == 1:
            self.deck_draw = [deck[0].id,]
        else:
            self.deck_draw = [i.id for i in sample(deck, 2)]
        self.save()


class FlightGroup(models.Model):
    name = models.CharField(max_length=20)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='flight_groups')
    arrival = models.SmallIntegerField(default=1)
    vector = models.CharField(max_length=6)

    ORDERS_CHOICES = (
        ('A', 'Attack'),
        ('S', 'Strike'),
        ('E', 'Escort'),
        ('X', 'Special')
    )
    orders = models.CharField(max_length=1, choices=ORDERS_CHOICES, default="A")

    class Meta:
        verbose_name = 'Flight Group'
        verbose_name_plural = 'Flight Groups'

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

    def batch_load(self, setup_list):
        """setup_list should be a list of 6 tuples in (chassis_id, init, action)
           any can be null, we just make some assumptions for those.
           The index of each tuple corresponds to the player count.
        """
        players = 1
        default = (self.mission.enemy_faction.default_ship.id, 1, 'A')
        for s in setup_list:
            if not s: s = default
            action = s[2]
            init = s[1]
            chassis = s[0]
            self.mission.fgsetup_set.create(flight_group=self, chassis_id=chassis, action=action, players=players, init=init)


class FGSetup(models.Model):
    action = models.CharField(max_length=1, choices=( ('A', 'Add'), ('R', 'Replace') ), default='A')
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE, null=True, blank=True)
    flight_group = models.ForeignKey(FlightGroup, on_delete=models.CASCADE, related_name='squad_members')
    players = models.SmallIntegerField(default=1)
    init = models.SmallIntegerField(default=1)
    elite = models.BooleanField(default=False)
    enemy = models.ForeignKey(EnemyPilot, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Squad Member'
        verbose_name_plural = 'Squad Members'
        indexes = [
            models.Index(fields=['players']),
            models.Index(fields=['init'])
        ]

    def __str__(self):
        return self.chassis.name if self.chassis else 'Random'

    @cached_property
    def is_default(self):
        return self.chassis == self.flight_group.mission.enemy_faction.default_ship

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


class Ally(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='allies')
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE)
    callsign = models.CharField(max_length=35)
    initiative = models.PositiveSmallIntegerField(default=1)
    abilities = models.ManyToManyField(Card, limit_choices_to={'ai_description__isnull':False}, blank=True)

    class Meta:
        verbose_name_plural = 'Allies'

    def __str__(self):
        return self.callsign

    @cached_property
    def pilot(self):
        return '{} ({})'.format(self.callsign, self.chassis)
