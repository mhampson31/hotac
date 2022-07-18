from django.test import TestCase

from xwtools.models import Chassis
from campaign.models import PlayableShip, MissionFeature, Campaign

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

