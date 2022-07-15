from django.test import TestCase

from xwtools.models import Dial, DialManeuver, Chassis, ArcDirectionChoice, RangeChoice
from .models import AI, AIManeuver, Rulebook, UpgradeLogic

# Create your tests here.


def create_ai_test_data(flee=1):
    rulebook = Rulebook.objects.create(description="AI Rules", upgrade_logic=UpgradeLogic.HOTAC, initiative_progression=UpgradeLogic.HOTAC)
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



