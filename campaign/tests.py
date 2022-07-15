from django.test import TestCase
from campaign.models.campaigns import PlayableShip

from xwtools.models import Dial, DialManeuver, Chassis, ArcDirectionChoice, RangeChoice, Faction
from .models import AI, AIManeuver, Rulebook, UpgradeLogic, PlayableShip, MissionFeature, Mission, Campaign

# Create your tests here.

def create_rulebook_data(desc):
    return Rulebook.objects.create(description=desc, upgrade_logic=UpgradeLogic.HOTAC, initiative_progression=UpgradeLogic.HOTAC)

def create_mission_data(rulebook):
    chassis = Chassis.objects.create(name="T-Wing")
    enemy = Faction.objects.create(name="Test Navy", default_ship=chassis)
    return Mission.objects.create(name="Test Mission", story="Test of the Aturi Cluster", sequence=1,
                                  rulebook=rulebook, enemy_faction=enemy)


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
        #self.assertEqual(self.rulebook.xp_share, 0)
        # Why does Rulebook have this method? Doesn't make a lot of sense...
        self.assertRaises(self.rulebook.xp_share, AttributeError)

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
        # FeatureChoices isn't exposed for import, so hard-coding the FeatureChoice types here.
        # These are unlikely to change.
        cls.feature_1 = MissionFeature.objects.create(name="rock", type='O')
        cls.feature_2 = MissionFeature.objects.create(name="turret", type='E')

    def test_str(self):
        self.assertEqual(self.feature_1.__str__(), "rock")

    def test_is_emplacement(self):
        self.assertFalse(self.feature_1.is_emplacement)
        self.assertTrue(self.feature_2.is_emplacement)


class MissionTest(TestCase):
    def test_str(self):
        mission = create_mission_data(rulebook=create_rulebook_data("Test Rules"))
        self.assertEqual(mission.__str__(), "Test Mission (Test of the Aturi Cluster 1)")


class CampaignTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        rulebook = create_rulebook_data("Campaign Rules")
        cls.mission = create_mission_data(rulebook)
        cls.campaign = Campaign.objects.create(rulebook=rulebook, description="Testers of the Aturi Cluster")
        cls.campaign.starting_deck()
        # add sessions

    def test__str(self):
        self.assertEqual(self.campaign.__str__(), "Testers of the Aturi Cluster")

    def test_victory_points(self):
        pass

    def test_xp_share(self):
        pass

    def test_limited_upgrades(self):
        from .models import PilotUpgrade
        upgrades = PilotUpgrade.objects.filter(pilot__campaign=self.campaign, card__limited=True).values_list('card__name', flat=True)
        pass

    def test_starting_deck(self):
        self.assertQuerysetEqual(self.campaign.deck.all(), [self.mission,])


    def test_draw_missions(self):
        # if the starter mission is in the deck, return it
        # if only one thing is in the deck, return it
        # else, return two options
        # set deck_draw to that
        pass

