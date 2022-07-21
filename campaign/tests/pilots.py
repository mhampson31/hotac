from django.test import TestCase

from campaign.models import User, Campaign, Pilot, PilotShip, PilotUpgrade, PlayableShip
from xwtools.models import Chassis, Card, SlotChoice

from .utilities import create_rulebook_data, create_pilot_data


class PilotTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.pilot = create_pilot_data(callsign='Tester')
        # Path A and path F

    def test_str(self):
        self.assertEqual(self.pilot.__str__(), "Tester (Player)")

    def total_xp(self):
        # base + earned + self.bonus_xp
        pass

    def spent_xp(self):
        # self.spent_ships + self.spent_upgrades + self.spent_initiative
        pass

    def spent_ships(self):
        # (self.ships.count() - 1) * self.campaign.rulebook.ship_cost
        pass

    def spent_upgrades(self):
        # sum([u.cost for u in self.upgrades.all()])
        pass

    def spent_initiative(self):
        # sum([init_cost(init) for init in range(self.campaign.rulebook.start_init+1, self.initiative+1)])
        pass

    def active_ship(self):
        # grab the active ship. If there's somehow multiple, grab the newest
        # self.pilotship_set.filter(active=True).last()
        pass

    def starter_ship(self):
        # self.ships.first()
        pass

    def slots(self):
        """
        Compile the list of slots available to a player, according to their
        active ship's defaults, their initiative, their chosen progression path,
        and their ship's progression path
        """
        # slot_list
        pass

    def available_upgrades(self):
        # The upgrade list queryset takes some assembly.
        # First, grab all the CampaignUpgrades that the players has slots for
        # (Those missing descriptions are assumed to be AI-only abilities)

        # Next, exclude any the player already has, unless they're marked as repeatable

        # Then exclude any Pilot upgrades belonging to a different faction

        # Finally, put everything in order

        # upgrade_query
        pass

    def force_charges(self):
        """
        A pilot's Force charges equals the count of Force upgrades plus the Force charges
        on other cards, to a max of 3.
        HotAC rules as written don't seem to account for cards like Ezra (gunner)
        but we're counting them here.
        """
        pass

    def kills(self):
        # Chassis.objects.filter(enemypilot__sessionenemy__killed_by__pilot=self).annotate(Count('id'))
        pass


class PilotShipTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        chassis = Chassis.objects.create(name="Ship Ship", hull=3, shields=0)
        pilot_1 = create_pilot_data("Shipper 1")
        pilot_2 = create_pilot_data("Shipper 2")

        cls.playable_ship = PlayableShip.objects.create(rulebook=pilot_1.campaign.rulebook, chassis=chassis)
        cls.ship_1 = PilotShip.objects.create(pilot=pilot_1, chassis=chassis)
        cls.ship_2 = PilotShip.objects.create(pilot=pilot_2, chassis=chassis, name="Ship Name")

        great_card = Card.objects.create(name="Plot Armor", type=SlotChoice.MODIFICATION, adds="+[Shield] +[Hull]")
        hull_card = Card.objects.create(name="Not Bad", type=SlotChoice.MODIFICATION, adds="+[Hull]")
        shield_card = Card.objects.create(name="Mega Shield", type=SlotChoice.MODIFICATION, adds="+[Shield]")
        bad_card = Card.objects.create(name="Red Shirt", type=SlotChoice.MODIFICATION, adds="-[Shield] -[Hull]")

        PilotUpgrade.objects.create(pilot=pilot_1, card=great_card, status='U', cost=1)
        PilotUpgrade.objects.create(pilot=pilot_1, card=hull_card, status='U', cost=1)
        PilotUpgrade.objects.create(pilot=pilot_1, card=shield_card, status='U', cost=1)
        PilotUpgrade.objects.create(pilot=pilot_1, card=bad_card, status='U', cost=1)

        PilotUpgrade.objects.create(pilot=pilot_2, card=bad_card, status='U', cost=1)


    def test_str(self):
        self.assertEqual(self.ship_1.__str__(), "Shipper 1's Ship Ship")
        # I didn't think this through when coming up with test names but we'll go with it
        self.assertEqual(self.ship_2.__str__(), "Shipper 2's Ship Ship Ship Name")

    def test_game_info(self):
        self.assertEqual(self.ship_1.game_info, self.playable_ship)
        self.assertEqual(self.ship_2.game_info, self.playable_ship)


    def test_shields(self):
        """ Test adding and removing shield upgrades to ensure the ship's game values
            are being calculated correctly.
            PilotShip.shields is a cached property so we need to clear it with each check.
        """
        # Pilot 2 has no shields and no upgrades
        self.assertEqual(self.ship_2.shields, 0)
        del self.ship_2.shields

        # Shields can't go below 0
        self.ship_2.pilot.upgrades.filter(card__name="Red Shirt").update(status='E')
        self.assertEqual(self.ship_2.shields, 0)


        # Pilot 1 equips some upgrades one by one
        # Shield +1, Hull +1
        self.ship_1.pilot.upgrades.filter(card__name="Plot Armor").update(status='E')
        self.assertEqual(self.ship_1.shields, 1)
        del self.ship_1.shields

        # Hull-only, no effect on shields
        self.ship_1.pilot.upgrades.filter(card__name="Not Bad").update(status='E')
        self.assertEqual(self.ship_1.shields, 1)
        del self.ship_1.shields

        # Shield +1
        self.ship_1.pilot.upgrades.filter(card__name="Mega Shield").update(status='E')
        self.assertEqual(self.ship_1.shields, 2)
        del self.ship_1.shields

        # Shield -1
        self.ship_1.pilot.upgrades.filter(card__name="Red Shirt").update(status='E')
        self.assertEqual(self.ship_1.shields, 1)


    def test_hull(self):
        """ Test adding and removing hull upgrades to ensure the ship's game values
            are being calculated correctly.
            PilotShip.hull is a cached property so we need to clear it with each check.
        """
        # Pilot 2 has no shields and no upgrades
        self.assertEqual(self.ship_2.hull, 3)
        del self.ship_2.hull

        self.ship_2.pilot.upgrades.filter(card__name="Red Shirt").update(status='E')
        self.assertEqual(self.ship_2.hull, 2)

        # Pilot 1 equips some upgrades one by one
        # Shield +1, Hull +1
        self.ship_1.pilot.upgrades.filter(card__name="Plot Armor").update(status='E')
        self.assertEqual(self.ship_1.hull, 4)
        del self.ship_1.hull

        # Hull +1
        self.ship_1.pilot.upgrades.filter(card__name="Not Bad").update(status='E')
        self.assertEqual(self.ship_1.hull, 5)
        del self.ship_1.hull

        # Shield +1, no effect on hull
        self.ship_1.pilot.upgrades.filter(card__name="Mega Shield").update(status='E')
        self.assertEqual(self.ship_1.hull, 5)
        del self.ship_1.hull

        # Hull -1
        self.ship_1.pilot.upgrades.filter(card__name="Red Shirt").update(status='E')
        self.assertEqual(self.ship_1.hull, 4)


class PilotUpgradeTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # pilot, card, status, cost
        cls.pilot = create_pilot_data(callsign="Upgrader 1")


