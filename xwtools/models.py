from django.db import models
from django.db.models import Case, When, Value
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

import re


class SlotChoice(models.TextChoices):
    TALENT = 'TLN', _('Talent')
    ASTROMECH = 'AST', _('Astromech')
    CANNON = 'CNN', _('Cannon')
    CONFIG = 'CNF', _('Config')
    CREW = 'CRW', _('Crew')
    DEVICE = 'DVC', _('Device')
    FORCE = 'FRC', _('Force Power')
    PILOT = 'PLT', _('Pilot') # TAKES TALENTS, FORCE, AND PILOT UPGRADES
    GUNNER = 'GNR', _('Gunner')
    ILLICIT = 'ILC', _('Illicit')
    MISSILE = 'MSL', _('Missile')
    MODIFICATION = 'MOD', _('Modification')
    SENSOR = 'SNS', _('Sensor')
    RELAY = 'TAC', _('Tactical Relay')
    TECH = 'TCH', _('Tech')
    TORPEDO = 'TRP', _('Torpedo')
    TITLE = 'TTL', _('Title')
    TURRET = 'TRT', _('Turret')
    SHIP = 'SHP', _('Ship')
    COMMAND = 'COM', _('Command')
    HARDPOINT = 'HRD', _('Hardpoint')
    CARGO = 'CRG', _('Cargo')
    TEAM = 'TEM', _('Team')


class DifficultyChoice(models.TextChoices):
    BLUE = 'B', _('Blue')
    WHITE = 'W', _('White')
    RED = 'R', _('Red')
    PURPLE = 'P', _('Purple')


class SizeChoice(models.TextChoices):
    SMALL = 'S', _('Small')
    MEDIUM = 'M', _('Medium')
    LARGE = 'L', _('Large')
    HUGE = 'H', _('Huge')


class ArcChoice(models.TextChoices):
    FRONT = 'F', _('Front Arc')
    REAR = 'R', _('Rear Arc')
    TURRET = 'T', _('Single Turret Arc')
    DOUBLE_TURRET = 'TT', _('Double Turret Arc')
    FULL_FRONT = 'FF', _('Full Front Arc')
    FULL_REAR = 'RR', _('Full Rear Arc')
    BULLSEYE = 'B', _('Bullseye Arc')
    LEFT = 'SL', _('Left Arc')
    RIGHT = 'SR', _('Right Arc')


class ActionChoice(models.TextChoices):
    BARREL_ROLL = 'BRO', _('Barrel Roll')
    BOOST = 'BST', _('Boost')
    CALCULATE = 'CLT', _('Calculate')
    CLOAK = 'CLK', _('Cloak')
    COORDINATE = 'CRD', _('Coordinate')
    EVADE = 'EVD', _('Evade')
    FOCUS = 'FCS', _('Focus')
    LOCK = 'LCK', _('Lock')
    JAM = 'JAM', _('Jam')
    RELOAD = 'RLD', _('Reload')
    REINFORCE = 'RNF', _('Reinforce')
    ROTATE = 'RTT', _('Rotate Arc')
    SLAM = 'SLM', _('SLAM')


class RangeChoice(models.TextChoices):
    RANGE_12 = '1', 'R1/R2 Closing'
    RANGE_23 = '2', 'R3/R2 Fleeing'
    RANGE_4 = '3', 'R4+'
    STRESSED = '4', 'Stressed'
    HYPERSPACE = '5', 'Hyperspace'
    DECLOAK = '6', 'Decloak'


class ArcDirectionChoice(models.TextChoices):
    BE = 'BE', 'Bullseye'
    FR = 'FR', 'Front (Right)'
    RF = 'RF', 'Right (Front)'
    RA = 'RA', 'Right (Rear)'
    AR = 'AR', 'Rear (Right)'
    FL = 'FL', 'Front (Left)'
    LF = 'LF', 'Left (Front)'
    LA = 'LA', 'Left (Rear)'
    AL = 'AL', 'Rear (Left)'
    SP = 'SP', 'Special'


class LimitedChoice(models.IntegerChoices):
    GENERIC = 0, _('')
    UNIQUE = 1, _('•')
    UNIQUE2 = 2, _('••')
    UNIQUE3 = 3, _('•••')


class Faction(models.Model):
    name = models.CharField(max_length=20)
    ships = models.ManyToManyField('Chassis')
    default_ship = models.OneToOneField('Chassis', on_delete=models.CASCADE, related_name='default_for')

    def __str__(self):
        return self.name


class Card(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    ai_description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=3, choices=SlotChoice.choices)
    type2 = models.CharField(max_length=3, choices=SlotChoice.choices, null=True, blank=True, default=None)
    charges = models.PositiveSmallIntegerField(null=True, blank=True)
    recurring = models.BooleanField(default=False)
    force = models.BooleanField(default=False)
    cost = models.SmallIntegerField(default=0)
    repeat = models.BooleanField(default=False)
    initiative = models.PositiveSmallIntegerField(default=1, null=True)
    chassis = models.ForeignKey('Chassis', on_delete=models.CASCADE, null=True, blank=True)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE, null=True, blank=True)
    adds = models.CharField(max_length=120, blank=True, null=True)
    requires = models.CharField(max_length=120, blank=True, null=True)
    limited = models.SmallIntegerField(default=LimitedChoice.GENERIC, choices=LimitedChoice.choices)
    player_use = models.BooleanField(default=True)
    ai_use = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['force']),
            models.Index(fields=['initiative']),
            models.Index(fields=['chassis']),
            models.Index(fields=['faction']),
            models.Index(fields=['player_use'])
        ]
        ordering = ['type', 'name']


    def __str__(self):
        name = '{}{}'.format(self.get_limited_display(), self.name)
        if self.type == SlotChoice.PILOT.value:
            return '{} - {}'.format(name, self.chassis)
        else:
            return name

    def campaign_cost(self, upgrade_logic):
        # todo: this needs to point to UpgradeLogic
        if upgrade_logic == 1:
            cost = self.cost
            if self.type == SlotChoice.PILOT:
                cost = self.initiative
                if self.force:
                    m = self.charges + 3
                else:
                    m = 2
            elif self.type in (SlotChoice.TALENT, SlotChoice.FORCE):
                m = 2
            else:
                m = 1
            return cost * m


class Attack(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE)
    arc = models.CharField(max_length=2, choices=ArcChoice.choices, default=ArcChoice.FRONT.value)
    dice = models.PositiveSmallIntegerField(default=3)
    range = models.CharField(max_length=3)
    ordnance = models.BooleanField(default=False)

# ### proxy managers ### #

class UpgradeCardManager(models.Manager):
    def get_queryset(self):
        return super(UpgradeCardManager, self).get_queryset().exclude(type__in=[SlotChoice.PILOT.value, SlotChoice.SHIP.value])


class PilotCardManager(models.Manager):
    def get_queryset(self):
        return super(PilotCardManager, self).get_queryset().filter(type=SlotChoice.PILOT.value)


class ShipAbilityManager(models.Manager):
    def get_queryset(self):
        return super(ShipAbilityManager, self).get_queryset().filter(type=SlotChoice.SHIP.value)


class UpgradeCard(Card):
    objects = UpgradeCardManager()

    class Meta:
        proxy = True


class PilotCard(Card):
    objects = PilotCardManager()

    class Meta:
        proxy = True


class ShipAbility(Card):
    objects = ShipAbilityManager()

    class Meta:
        proxy = True
        verbose_name_plural = 'Ship Abilities'


class Dial(models.Model):
    chassis = models.OneToOneField('Chassis', on_delete=models.SET_NULL, null=True, related_name='dial')

    def __str__(self):
        if self.chassis:
            return self.chassis.name
        else:
            return '--'

    @property
    def css_name(self):
        return re.sub(r'[^\w\d]', '', self.chassis.name.lower())

    @property
    def max_speed(self):
        return self.maneuvers.aggregate(speed=models.Max('speed'))['speed']

    @property
    def dial_width(self):
        speeds = {}
        for s in self.maneuvers.values_list('speed', flat=True):
            speeds[s] = speeds.get(s, 0) + 1
        return max(speeds.values())


class DialManeuver(models.Model):
    BEARING_TYPES = {
        'Straight': 'S',
        'Bank': 'B',
        'Turn': 'T',
        'K-Turn': 'KT',
        'Tallon Roll': 'TR',
        'Sloop': 'SL',
        'Reverse Bank': 'RB',
        'Stationary': 'SS',
        'Reverse Straight': 'RS',
        '--':'XX' # for use as a spacer
    }

    BEARING_CHOICES = [(v, k) for k, v in BEARING_TYPES.items()]

    DIRECTION_CHOICES = (
        ('L', 'Left'),
        ('R', 'Right')
    )

    bearing = models.CharField(max_length=3, choices=BEARING_CHOICES)
    dial = models.ForeignKey(Dial, on_delete=models.CASCADE, related_name='maneuvers')
    speed = models.SmallIntegerField() # negative values for reverse maneuvers
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES, null=True, blank=True)
    difficulty = models.CharField(max_length=1, choices=DifficultyChoice.choices, default='W')

    def find_mirror(self):
        if not self.direction:
            return self
        else:
            new_direction = {'L':'R', 'R':'L'}[self.direction]
            return self.dial.maneuvers.get(speed=self.speed, bearing=self.bearing, direction=new_direction)

    @property
    def css_name(self):
        if self.direction:
            return '{} {}'.format(self.get_bearing_display(), self.get_direction_display())
        else:
            return self.get_bearing_display()

    @property
    def icon_color(self):
        return {'B':'easy', 'R':'hard', 'W':'', 'P':'force'}[self.difficulty]

    def __str__(self):
        return '{} {}{}{}'.format(self.speed,
                                   self.get_bearing_display(),
                                   ' ' + self.get_direction_display() if self.direction else '',
                                   '' if self.difficulty == 'W' else ' ' + self.get_difficulty_display())

    class Meta:
        """
        The second order item is a case statement that attemps to create a left-center-right
        row of maneuvers. It starts with a positive value based on the bearing, with
        1 and 2 being the "center" values, and higher values being closer to the edge.
        Then, if the direction of the maneuver is Left, it flips the Case value to negative.
        The end result is a list of ordering values like LT=-4, LB=-3, straight=2, RB=3, RT=4
        """
        ordering = ['-speed', Case(
                When(bearing='XX', then=Value(1)),
                When(bearing='S', then=Value(2)),  # No speed can have more than one of
                When(bearing='RS', then=Value(2)), # these three bearings, so they can
                When(bearing='SS', then=Value(2)), # have the same value
                When(bearing='B', then=Value(3)),
                When(bearing='RB', then=Value(3)),
                When(bearing='T', then=Value(4)),
                When(bearing='TR', then=Value(5)),
                When(bearing='SL', then=Value(6)),
                When(bearing='KT', then=Value(8)),
                output_field=models.SmallIntegerField()) *
                Case(When(direction='L', then=Value(-1)),
                     default=Value(1),
                     output_field=models.SmallIntegerField())]


class Chassis(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=40, null=True, blank=True)

    size = models.CharField(max_length=1, choices=SizeChoice.choices, default=SizeChoice.SMALL)
    attack = models.PositiveSmallIntegerField(default=0)
    attack_arc = models.CharField(max_length=2, choices=ArcChoice.choices, default=ArcChoice.FRONT.value)
    attack2 = models.PositiveSmallIntegerField(default=0)
    attack2_arc = models.CharField(max_length=2, choices=ArcChoice.choices, null=True, blank=True)
    agility = models.PositiveSmallIntegerField(default=0)
    hull = models.PositiveSmallIntegerField(default=0)
    shields = models.PositiveSmallIntegerField(default=0)
    energy = models.PositiveSmallIntegerField(default=0)
    hyperdrive = models.BooleanField(default=True)

    walker = models.BooleanField(default=False)
    armor = models.PositiveSmallIntegerField(default=0)

    css = models.CharField(max_length=80, null=True, blank=True)

    ability = models.ForeignKey(Card, limit_choices_to={'type':SlotChoice.SHIP.value},
                                          null=True, blank=True, on_delete=models.SET_NULL,
                                          related_name='ship')

    class Meta:
        verbose_name_plural = 'Chassis'

    def __str__(self):
        return self.name

    @property
    def css_name(self):
        return self.css if self.css else self.slug.replace('-', '')


class Slot(models.Model):
    chassis = models.ForeignKey(Chassis, related_name='slots', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=SlotChoice.choices)
    initiative = models.PositiveSmallIntegerField(default=1)

    @property
    def css_name(self):
        return self.get_type_display()


class Action(models.Model):
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE, related_name='actions')
    action = models.CharField(max_length=3, choices=ActionChoice.choices)
    difficulty = models.CharField(max_length=1, choices=DifficultyChoice.choices, default=DifficultyChoice.WHITE)
    linked_action = models.CharField(max_length=3, choices=ActionChoice.choices, blank=True)
    linked_difficulty = models.CharField(max_length=1, choices=DifficultyChoice.choices, blank=True)

    def __str__(self):
        if self.linked_action:
            return '[{}#{}] [Linked] [{}#{}]'.format(self.get_action_display(), self.get_difficulty_display(), self.get_linked_action_display(), self.get_linked_difficulty_display())
        else:
            return '[{}#{}]'.format(self.get_action_display(), self.get_difficulty_display())

    @property
    def difficulty_css(self):
        return {'B':'easy', 'R':'hard', 'W':'', 'P':'force'}[self.difficulty]

    @property
    def linked_difficulty_css(self):
        return {'B':'easy', 'R':'hard', 'W':'', 'P':'force'}.get(self.linked_difficulty, '')
