from django.test import TestCase
from campaign.models.campaigns import PlayableShip

from xwtools.models import Dial, DialManeuver, Chassis, ArcDirectionChoice, RangeChoice
from .models import AI, AIManeuver, Rulebook, UpgradeLogic, PlayableShip, MissionFeature

# Create your tests here.

def create_rulebook_data(desc):
    return Rulebook.objects.create(description=desc, upgrade_logic=UpgradeLogic.HOTAC, initiative_progression=UpgradeLogic.HOTAC)

def create_ai_test_data(flee=1):
    rulebook = create_rulebook_data("AI Rules")
    shuttle = Chassis.objects.create(name="AI Shuttle")

    dial = Dial.objects.create(chassis=shuttle)
    dial_maneuvers = [
        DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Turn'], direction='L', speed=2, dial=dial),
        DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Straight'], speed=2, dial=dial),
        DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Turn'], direction='R', speed=2, dial=dial),
        DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Straight'], speed=3, dial=dial),
        DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Straight'], speed=4, dial=dial)
    ]
    ai = AI.objects.create(rulebook=rulebook, dial=dial, flee=flee)

    ai_maneuver = AIManeuver.objects.create(ai=ai, arc=ArcDirectionChoice.FR, range=RangeChoice.RANGE_12,
                            roll_1= dial_maneuvers[4], roll_2=dial_maneuvers[3], roll_3=dial_maneuvers[2],
                            roll_4=dial_maneuvers[2], roll_5=dial_maneuvers[2], roll_6=dial_maneuvers[2])

    return {'ai':ai, 'dial_maneuvers':dial_maneuvers, 'ai_maneuver':ai_maneuver}


class AITestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        data = create_ai_test_data()
        cls.ai = data['ai']

    def test_str(self):
        self.assertEqual(self.ai.__str__(), 'AI Shuttle AI')

    def test_mirror(self):
        # need a few right-sided AIManeuvers. Test that the AIManeuver set is symmetrical.
        pass

    def test_has_special(self):
        # test that has_special returns true if there's a Special maneuver in the set,
        # and false when there's not
        pass


class AIManeuverTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        data = create_ai_test_data()
        cls.ai = data['ai']
        cls.ai_maneuver = data['ai_maneuver']
        cls.dial_maneuvers = data['dial_maneuvers']

    def test_rolls(self):
        self.assertEqual(self.ai_maneuver.rolls, [self.dial_maneuvers[4], self.dial_maneuvers[3], self.dial_maneuvers[2],
                                      self.dial_maneuvers[2], self.dial_maneuvers[2], self.dial_maneuvers[2]])

    def test_arc_order(self):
        self.assertEqual(self.ai_maneuver.arc_order, 2)


class AIPriorityTest(TestCase):
    # AIPriority doesn't really have any business logic to test, but maybe it will someday
    def test_nothing(self):
        pass


class RulebookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.rulebook = create_rulebook_data("Rulebook")

    def test_str(self):
        self.assertEqual(self.rulebook.__str__(), "Rulebook")

    def test_xp_share(self):
        # this is obvious insufficient.
        # need to check that each pilot gets an equal share of the total earned XP
        self.assertEqual(self.rulebook.xp_share, 0)

    def test_hotac_initiative_cost(self):
        # only testing HotAC logic here. Add separate tests if we ever add more rulesets.
        self.assertEqual(self.rulebook.get_initiative_cost(2), 6)
        self.assertEqual(self.rulebook.get_initiative_cost(3), 9)
        self.assertEqual(self.rulebook.get_initiative_cost(4), 12)
        self.assertEqual(self.rulebook.get_initiative_cost(5), 15)
        self.assertEqual(self.rulebook.get_initiative_cost(6), 18)



class PlayableShipTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        rulebook = create_rulebook_data("Playable Ship Rules")
        chassis = Chassis.objects.create(name="Playable Ship")
        cls.ship = PlayableShip.objects.create(rulebook=rulebook, chassis=chassis)

    def test_name(self):
        self.assertEqual(self.ship.name, "Playable Ship")

    def test_str(self):
        self.assertEqual(self.ship.__str__(), "Playable Ship")



class MissionFeatureTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        from .models import FeatureChoice
        cls.feature_1 = MissionFeature.objects.create(name="rock", type=FeatureChoice.OBSTACLE)
        cls.feature_2 = MissionFeature.objects.create(name="turret", type=FeatureChoice.EMPLACEMENT)

    def test_str(self):


    def __str__(self):
        return self.name

    @cached_property
    def is_emplacement(self):
        return self.type == FeatureChoice.EMPLACEMENT

class Mission(models.Model):

    name = models.CharField(max_length=30)
    story = models.CharField(max_length=30)
    sequence = models.PositiveSmallIntegerField()
    rulebook = models.ForeignKey(Rulebook, on_delete=models.SET_NULL, null=True)

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
