from django.test import TestCase

from .models import Chassis, Faction, Card, SlotChoice, Dial, DialManeuver, DifficultyChoice


class FactionTestCase(TestCase):
    def setUp(self):
        Faction.objects.create(name="Test Faction")


class ChassisTestCase(TestCase):
    def setUp(self):
        self.twing = Chassis.objects.create(name="T-Wing", slug="t-wing", attack=3, agility=2, hull=4, shields=2)
        self.tie = Chassis.objects.create(name="TIE Tester", slug="tie-tester", attack=2, agility=3, hull=3, css="Random CSS")

    def test_css_name(self):
        self.assertEqual(self.twing.css_name, "twing")
        self.assertEqual(self.tie.css_name, "Random CSS")


class CardTestCase(TestCase):
    def setUp(self):
        boat = Chassis.objects.create(name="CardBoat")
        self.droid = Card.objects.create(name="T3-ST", type=SlotChoice.ASTROMECH, cost=7, limited=1)
        self.talent = Card.objects.create(name="Talent", type=SlotChoice.TALENT, cost=2)
        self.force = Card.objects.create(name="Force Upgrade", type=SlotChoice.FORCE, cost=3)
        self.pilot = Card.objects.create(name="Pilot", type=SlotChoice.PILOT, initiative=4, chassis=boat)
        self.jedi = Card.objects.create(name="Force Pilot", type=SlotChoice.PILOT, initiative=4, force=True, charges=2, chassis=boat)

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

        # dial with 4 straight, 3 straight, 2 l/s/r
        # Max speed of 4, width of 3
        DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Turn'], direction='L', speed=2, dial=self.dial)
        DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Straight'], speed=2, dial=self.dial)
        DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Turn'], direction='R', speed=2, dial=self.dial)
        DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Straight'], speed=3, dial=self.dial)
        DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Straight'], speed=4, dial=self.dial)

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
        self.assertEqual(self.dial.max_speed, 4)

    def test_dial_width(self):
        # tests that we get the number of maneuvers of the speed with the most of them
        self.assertEqual(self.dial.dial_width, 3)


class DialManeuverTestCase(TestCase):
    def setUp(self):
        Dial.objects.create(chassis=None)
        dial = Dial.objects.last()
        # We need maneuvers with all three directions, and all four colors
        self.dm1 = DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Turn'], direction='L', speed=2, dial=dial)
        self.dm2 = DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Straight'], speed=2, dial=dial, difficulty=DifficultyChoice.BLUE)
        self.dm3 = DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Turn'], direction='R', speed=2, dial=dial)
        self.dm4 = DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Straight'], speed=3, dial=dial, difficulty=DifficultyChoice.RED)
        self.dm5 = DialManeuver.objects.create(bearing=DialManeuver.BEARING_TYPES['Straight'], speed=4, dial=dial, difficulty=DifficultyChoice.PURPLE)

    def test__str(self):
        self.assertEqual(self.dm1.__str__(), "2 Turn Left")
        self.assertEqual(self.dm2.__str__(), "2 Straight Blue")
        self.assertEqual(self.dm3.__str__(), "2 Turn Right")
        self.assertEqual(self.dm4.__str__(), "3 Straight Red")
        self.assertEqual(self.dm5.__str__(), "4 Straight Purple")


    def test_find_mirror(self):
        # dm1 and dm3 are mirrors of each other, but is it bad practice to use them this way?
        self.assertEqual(self.dm1.find_mirror(), self.dm3)
        self.assertEqual(self.dm2.find_mirror(), self.dm2)
        self.assertEqual(self.dm3.find_mirror(), self.dm1)

    def test_css_name(self):
        self.assertEqual(self.dm1.css_name, 'Turn Left')
        self.assertEqual(self.dm5.css_name, 'Straight')


    def test_icon_color(self):
        self.assertEqual(self.dm1.icon_color, '')
        self.assertEqual(self.dm2.icon_color, 'easy')
        self.assertEqual(self.dm4.icon_color, 'hard')
        self.assertEqual(self.dm5.icon_color, 'force')
