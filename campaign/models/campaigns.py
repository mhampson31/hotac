from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

from math import floor

from xwtools.models import Chassis, Faction, SlotChoice, Upgrade


class BaseChoice(models.TextChoices):
    PILOT = 'P', 'Pilot'
    UPGRADE = 'U', 'Upgrade'


class User(AbstractUser):
    pass


class Rulebook(models.Model):
    description = models.CharField(max_length=30)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ships = models.ManyToManyField(Chassis, through='PlayableShip')

    # player defaults
    start_init = models.SmallIntegerField(default=2)

    # configure a campaign's XP costs
    ship_cost = models.SmallIntegerField(default=5)

    class UpgradeLogic(models.IntegerChoices):
        HOTAC = 1, 'HotAC'

    upgrade_logic = models.IntegerField(choices=UpgradeLogic.choices)
    initiative_cost = models.SmallIntegerField(default=3)
    initiative_sq = models.BooleanField(default=False)

    starter_mission = models.ForeignKey('Mission', on_delete=models.SET_NULL, null=True, related_name='starts')

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('ruleset', kwargs={'pk': self.pk})

    def upgrade_cost(self, upgrade):
        """
        takes a CampaignUpgrade object and calculates the cost, based on the upgrade logic rules
        """
        if self.upgrade_logic == self.UpgradeLogic.HOTAC:
            if upgrade.base == BaseChoice.PILOT:
                if upgrade.force:
                    m = upgrade.charges + 3
                else:
                    m = 2
            elif upgrade.type in (SlotChoice.TALENT, SlotChoice.FORCE):
                m = 2
            else:
                m = 1
            return upgrade.cost * m

    @property
    def xp_share(self):
        pilots = 0
        xp = 0
        for s in self.session_set.all():
            pilots = pilots + s.pilots.count()
            xp = xp + s.xp_total
        return floor(xp/pilots)


class PlayableShip(models.Model):
    rulebook = models.ForeignKey(Rulebook, on_delete=models.CASCADE)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE)
    xp_value = models.SmallIntegerField(default = 0)

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
    rulebook = models.ForeignKey(Rulebook, on_delete=models.SET_NULL, null=True)
    turns = models.PositiveSmallIntegerField(default=12)

    objective = models.TextField()
    bonus_1 = models.TextField(blank=True, null=True)
    bonus_2 = models.TextField(blank=True, null=True)
    penalty = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{} ({} {})'.format(self.name, self.story, self.sequence)


class Campaign(models.Model):
    rulebook = models.ForeignKey(Rulebook, on_delete=models.SET_NULL, null=True)
    gm = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='campaign_gm')
    players = models.ManyToManyField(User)
    description = models.CharField(max_length=30)

    victory = models.PositiveSmallIntegerField()
    pool_xp = models.BooleanField(default=False)

    deck = models.ManyToManyField(Mission)
    deck_draw = models.JSONField(null=True)

    def __str__(self):
        return self.description

    @property
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

    def starting_deck(self):
        for m in Missions.objects.filter(rulebook=self.rulebook, sequence=1):
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


class CampaignUpgrade(models.Model):
    id = models.CharField(max_length=6, primary_key=True, db_index=False)
    base_id = models.IntegerField()
    base = models.CharField(max_length=1, choices=BaseChoice.choices)
    name = models.CharField(max_length=30)
    cost = models.IntegerField()
    description = models.CharField(max_length=255)
    ai_description = models.CharField(max_length=255)
    type = models.CharField(max_length=3, choices=SlotChoice.choices)
    type2 = models.CharField(max_length=3, choices=SlotChoice.choices, null=True, blank=True, default=None)
    charges = models.PositiveSmallIntegerField(null=True, blank=True)
    force = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'campaign_gameupgrades_v'
        managed = False


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
    orders = models.CharField(max_length=1, choices=ORDERS_CHOICES, default="A")

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
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE, null=True, blank=True)
    flight_group = models.ForeignKey(FlightGroup, on_delete=models.CASCADE, related_name='squad_members')
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
