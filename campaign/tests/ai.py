from django.test import TestCase

from .utilities import create_ai_test_data


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