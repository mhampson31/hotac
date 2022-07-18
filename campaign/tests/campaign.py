from django.test import TestCase

from xwtools.models import Chassis
from campaign.models import PlayableShip, MissionFeature, Campaign, FlightGroup, FGSetup, Ally

from .utilities import create_rulebook_data, create_mission_data


class RulebookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.rulebook = create_rulebook_data("Rulebook")

    def test_str(self):
        self.assertEqual(self.rulebook.__str__(), "Rulebook")

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
        from campaign.models import PilotUpgrade
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



class FlightGroupTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        mission = create_mission_data(rulebook=create_rulebook_data("Test Rules"))
        cls.flight_group = FlightGroup.objects.create(name="Alpha", mission=mission, arrival=1, vector=4)

    def test__str(self):
        self.assertEqual(self.flight_group.__str__, 'Alpha')

    def generate(self):
        # return a list with the correct enemies given the number of players and their group init
        # should test replacing default enemies with elite enemies
        # self.flight_group.generate(self, pilots, group_init)
        pass

    def batch_load(self):
        """setup_list should be a list of 6 tuples in (chassis_id, init, action)
           any can be null, we just make some assumptions for those.
           The index of each tuple corresponds to the player count.
        """
        # batch_load(self, setup_list)
        pass


class FGSetupTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        flight_group = FlightGroup.objects.create(name="Alpha", mission=mission, arrival=1, vector=4)
        mission = create_mission_data(rulebook=create_rulebook_data("Test Rules"))

        # A generic default enemy that always appears
        cls.fg_generic = FGSetup(chassis=mission.enemy_faction.default_chassis)

        # a random replacement for 3+ init and 2+ players
        cls.fg_replacement = FGSetup(action='R', chassis=None, players=2, init=3)

        # a second generic that appears at init 4+
        cls.fg_extra = FGSetup(chassis=mission.enemy_faction.default_chassis, init=4)

    def test__str(self):
        self.assertEqual(self.fg_generic.__str__(), 'T-Wing')
        self.assertEqual(self.fg_replacement.__str__(), 'Random')

    def test_default(self):
        self.assertTrue(self.fg_generic.is_default)
        self.assertFalse(self.fg_replacement.is_default)

    def generate(self, group_init):
        pass


class AllyTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        chassis = Chassis.objects.create(name="Ally Shuttle")
        mission = create_mission_data(rulebook=create_rulebook_data("Test Rules"))
        cls.ally = Ally.objects.create(mission=mission, chassis=chassis, callsign="Tester")

    def test_str(self):
        self.assertEqual(self.ally.__str__(), 'Tester')

    def test_pilot(self):
        self.assertEqual(self.ally.pilot, 'Tester (Ally Shuttle)')
        return '{} ({})'.format(self.callsign, self.chassis)

