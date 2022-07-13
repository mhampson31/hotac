from django.test import TestCase

from .models import Chassis, Faction, Card, SlotChoice, Dial, DialManeuver

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

        self.droid = Card.objects.get(name="T3-ST")
        self.talent = Card.objects.get(name="Talent")
        self.force = Card.objects.get(name="Force Upgrade")
        self.pilot = Card.objects.get(name="Pilot")
        self.jedi = Card.objects.get(name="Force Pilot")


    def test__str(self):
        self.assertEqual(self.droid.__str__(), '•T3-ST')
        self.assertEqual(self.talent.__str__(), 'Talent')
        self.assertEqual(self.jedi.__str__(), 'Force Pilot - CardBoat')

    def test_cost(self):
        # point costs are complex, depending on card type, Force abilities, and so on
        self.assertEqual(self.droid.campaign_cost(1), 7) # cost x1
        self.assertEqual(self.talent.campaign_cost(1), 4) # cost x2
        self.assertEqual(self.force.campaign_cost(1), 6) # cost x2
        self.assertEqual(self.pilot.campaign_cost(1), 8) # initiatve x2
        self.assertEqual(self.jedi.campaign_cost(1), 20) # initiatve x (charges + 3)


class DialTestCase(TestCase):
    def setUp(self):
        Chassis.objects.create(name="Dial Shuttle")
        shuttle = Chassis.objects.get(name="Dial Shuttle")

        Dial.objects.create(chassis=shuttle)
        self.dial = Dial.objects.first()

        Dial.objects.create(chassis=None)
        self.other_dial = Dial.objects.last()

    def test__str(self):
        self.assertEqual(self.dial.__str__(), "Dial Shuttle")
        self.assertEqual(self.other_dial.__str__(), "--")

    def test_css_name(self):
        # tests that we get the chassis name lower-cased and stripped of non-letters
        self.assertEqual(self.dial.css_name, "dialshuttle") #re.sub(r'[^\w\d]', ''

    def test_max_speed(self):
        # tests that we get the greatest speed value on the dial
        self.assertEqual(self.dial.max_speed, 1)

    def test_dial_width(self):
        # tests that we get the number of maneuvers of the speed with the most of them
        self.assertEqual(self.dial.dial_width, 1)

