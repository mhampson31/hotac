from django.test import TestCase

from .models import Chassis, Faction, Card, SlotChoice

# Create your tests here.



#Faction
#Card



class FactionTestCase(TestCase):
    def setUp(self):
        Faction.objects.create(name="Test Faction")


class ChassisTestCase(TestCase):
    def setUp(self):
        Chassis.objects.create(name="T-Wing", slug="t-wing", attack=3, agility=2, hull=4, shields=2)
        Chassis.objects.create(name="TIE Tester", slug="tie-tester", attack=2, agility=3, hull=3, css="Random CSS")

    def test_css_name(self):
        twing = Chassis.objects.get(name="T-Wing")
        tie = Chassis.objects.get(name="TIE Tester")
        self.assertEqual(twing.css_name, "twing")
        self.assertEqual(tie.css_name, "Random CSS")


class CardTestCase(TestCase):
    def setUp(self):
        Chassis.objects.create(name="CardBoat")
        boat = Chassis.objects.get(name="CardBoat")
        Card.objects.create(name="T3-ST", type=SlotChoice.ASTROMECH, cost=7, limited=1)
        Card.objects.create(name="Talent", type=SlotChoice.TALENT, cost=2)
        Card.objects.create(name="Force Upgrade", type=SlotChoice.FORCE, cost=3)
        Card.objects.create(name="Pilot", type=SlotChoice.PILOT, initiative=4, chassis=boat)
        Card.objects.create(name="Force Pilot", type=SlotChoice.PILOT, initiative=4, force=True, charges=2, chassis=boat)


    def test__str(self):
        droid = Card.objects.get(name="T3-ST")
        talent = Card.objects.get(name="Talent")
        jedi = Card.objects.get(name="Force Pilot")

        self.assertEqual(droid.__str__(), '•T3-ST')
        self.assertEqual(talent.__str__(), 'Talent')
        self.assertEqual(jedi.__str__(), 'Force Pilot - CardBoat')


    def test_cost(self):
        droid = Card.objects.get(name="T3-ST")
        talent = Card.objects.get(name="Talent")
        force = Card.objects.get(name="Force Upgrade")
        pilot = Card.objects.get(name="Pilot")
        jedi = Card.objects.get(name="Force Pilot")

        self.assertEqual(droid.campaign_cost(1), 7) # cost x1
        self.assertEqual(talent.campaign_cost(1), 4) # cost x2
        self.assertEqual(force.campaign_cost(1), 6) # cost x2
        self.assertEqual(pilot.campaign_cost(1), 8) # initiatve x2
        self.assertEqual(jedi.campaign_cost(1), 20) # initiatve x (charges + 3)
