from xwtools.models import Dial, DialManeuver, Chassis, ArcDirectionChoice, RangeChoice, Faction
from campaign.models import AI, AIManeuver, Rulebook, UpgradeLogic, Mission


def create_rulebook_data(desc):
    return Rulebook.objects.create(description=desc, upgrade_logic=UpgradeLogic.HOTAC, initiative_progression=UpgradeLogic.HOTAC)

def create_mission_data(rulebook):
    chassis = Chassis.objects.create(name="T-Wing")
    enemy = Faction.objects.create(name="Test Navy", default_ship=chassis)
    return Mission.objects.create(name="Test Mission", story="Test of the Aturi Cluster", sequence=1,
                                  rulebook=rulebook, enemy_faction=enemy)


def create_ai_test_data(flee=1):
    rulebook = create_rulebook_data("AI Rules")
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

