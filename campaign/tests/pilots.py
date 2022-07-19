from django.test import TestCase

from campaign.models import User, Campaign, Pilot, PilotShip, PilotUpgrade
from xwtools.models import Chassis

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
        chassis = Chassis.objects.create(name="Ship Ship")
        pilot_1 = create_pilot_data("Shipper 1")
        pilot_2 = create_pilot_data("Shipper 2")
        cls.ship_1 = PilotShip.objects.create(pilot=pilot_1, chassis=chassis)
        cls.ship_2 = PilotShip.objects.create(pilot=pilot_2, chassis=chassis, name="Ship Name")

    def test_str(self):
        self.assertEqual(self.ship_1.__str__(), "Shipper 1's Ship Ship")
        self.assertEqual(self.ship_2.__str__(), "Shipper 2's Ship Ship Ship Name")

    def game_info(self):
        # self.pilot.campaign.rulebook.playableship_set.get(chassis=self.chassis)
        pass

    def shields(self):
        # with shield upgrade equipped
        # with -shield upgrade equipped
        pass

    def hull(self):
        # with hull upgrade
        # with - hull upgrade
        pass


class PilotUpgradeTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # pilot, card, status, cost
        cls.pilot = create_pilot_data(callsign="Upgrader 1")


