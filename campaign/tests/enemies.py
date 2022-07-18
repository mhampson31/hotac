from django.test import TestCase

from xwtools.models import SizeChoice, Card, SlotChoice, Chassis, Faction

from .utilities import create_rulebook_data
from campaign.models import EnemyPilot, EnemyAbility

class EnemyPilotTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        chassis = Chassis.objects.create(name="Enemy Ship")
        other_chassis = Chassis.objects.create(name="Other Enemy Ship", size=SizeChoice.LARGE)
        faction = Faction.objects.create(name="Enemy Navy", default_ship=chassis)

        cls.default_pilot = EnemyPilot.objects.create(chassis=chassis, faction=faction)
        cls.other_pilot = EnemyPilot.objects.create(chassis=other_chassis, faction=faction)

        droid = Card.objects.create(name="T3-ST", type=SlotChoice.ASTROMECH, cost=7, limited=1)
        talent = Card.objects.create(name="Talent", type=SlotChoice.TALENT, cost=2)
        torpedo = Card.objects.create(name="Torpedo", type=SlotChoice.TORPEDO, cost=3)

        cls.named_pilot = EnemyPilot.objects.create(chassis=other_chassis, faction=faction, name_override="Darth Tester")

        EnemyAbility.objects.create(pilot=cls.default_pilot, card=droid, level=1)

        EnemyAbility.objects.create(pilot=cls.other_pilot, card=droid, level=1)
        EnemyAbility.objects.create(pilot=cls.other_pilot, card=talent, level=3)
        EnemyAbility.objects.create(pilot=cls.other_pilot, card=torpedo, level=5)

        EnemyAbility.objects.create(pilot=cls.named_pilot, card=talent, level=2)
        EnemyAbility.objects.create(pilot=cls.named_pilot, card=torpedo, level=2)
        EnemyAbility.objects.create(pilot=cls.named_pilot, card=droid, level=4)

    def test_str(self):
        self.assertEqual(self.default_pilot.__str__(), "Enemy Ship")
        self.assertEqual(self.other_pilot.__str__(), "Other Enemy Ship - Torpedo") # in5
        self.assertEqual(self.named_pilot.__str__(), "Other Enemy Ship - Darth Tester")

    def test_ability_list(self, lvl=1):
        # One ability
        self.assertEqual(self.default_pilot.ability_list(), 'T3-ST')

        # Multiple abilities, but not the higher-level ones
        self.assertEqual(self.named_pilot.ability_list(lvl=3), 'Talent/Torpedo')

        # All abilities
        self.assertEqual(self.other_pilot.ability_list(lvl=5), 'T3-ST/Talent/Torpedo')

    def test_basic(self):
        self.assertEqual(self.other_pilot.basic, 'T3-ST')

    def test_elite(self):
        # No abilities
        self.assertEqual(self.other_pilot.elite, '')

        # Multiple abilities at that level
        self.assertEqual(self.named_pilot.elite, 'Talent/Torpedo')

    def test_in3(self):
        self.assertEqual(self.other_pilot.in3, 'Talent')

    def test_in4(self):
        self.assertEqual(self.other_pilot.in4, '')
        self.assertEqual(self.named_pilot.in4, 'T3-ST')

    def test_in5(self):
        self.assertEqual(self.other_pilot.in5, 'Torpedo')

    def test_non_default_ship(self):
        self.assertFalse(self.default_pilot.non_default_ship)
        self.assertTrue(self.other_pilot.non_default_ship)

    def test_large_ship(self):
        self.assertFalse(self.default_pilot.large_ship)
        self.assertTrue(self.other_pilot.large_ship)


class EnemyAbilityTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        chassis = Chassis.objects.create(name="Enemy Ship")
        faction = Faction.objects.create(name="Enemy Navy", default_ship=chassis)

        droid = Card.objects.create(name="T3-ST", type=SlotChoice.ASTROMECH, cost=7, limited=1)
        talent = Card.objects.create(name="Talent", type=SlotChoice.TALENT, cost=2)

        pilot = EnemyPilot.objects.create(chassis=chassis, faction=faction)

        cls.ability_1 = EnemyAbility.objects.create(pilot=pilot, card=droid)
        cls.ability_5 = EnemyAbility.objects.create(pilot=pilot, card=talent, level=5)

    def test_str(self):
        self.assertEqual(self.ability_1.__str__(), "T3-ST")