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


DIFFICULTY_CHOICES = (
        ('B', 'Blue'),
        ('W', 'White'),
        ('R', 'Red'),
        ('P', 'Purple')
)


class SizeChoice(models.TextChoices):
    SMALL = 'S', _('Small')
    MEDIUM = 'M', _('Medium')
    LARGE = 'L', _('Large')
    HUGE = 'H', _('Huge')


class ArcChoice(models.TextChoices):
    FRONT = 'F', _('Front')
    REAR = 'R', _('Rear')
    TURRET = 'T', _('Turret')
    DOUBLE_TURRET = 'TT', _('Double Turret')
    FULL_FRONT = 'FF', _('Full Front')
    FULL_REAR = 'RR', _('Full Rear')
    BULLSEYE = 'B', _('Bullseye')
    LEFT = 'SL', _('Left')
    RIGHT = 'SR', _('Right')


class Faction(models.Model):
    name = models.CharField(max_length=20)
    ships = models.ManyToManyField('Chassis')
    default_ship = models.OneToOneField('Chassis', on_delete=models.CASCADE, related_name='default_for')

    def __str__(self):
        return self.name


class Ability(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    ai_description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=3, choices=SlotChoice.choices)
    type2 = models.CharField(max_length=3, choices=SlotChoice.choices, null=True, blank=True, default=None)
    charges = models.PositiveSmallIntegerField(null=True, blank=True)
    #recurring = models.BooleanField(default=False)
    force = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ['type', '-type2', 'name']

    def __str__(self):
        return self.name

    @property
    def for_players(self):
        return not self.description is None

    @property
    def for_ai(self):
        return not self.ai_description is None


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
    adds = models.CharField(max_length=120, blank=True, null=True)
    initiative = models.PositiveSmallIntegerField(default=1, null=True)
    chassis = models.ForeignKey('Chassis', on_delete=models.CASCADE, null=True, blank=True)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name



class UpgradeCardManager(models.Manager):
    def get_queryset(self):
        return super(UpgradeCardManager, self).get_queryset().exclude(type=SlotChoice.PILOT.value)


class PilotCardManager(models.Manager):
    def get_queryset(self):
        return super(PilotCardManager, self).get_queryset().filter(type=SlotChoice.PILOT.value)


class UpgradeCard(Card):
    objects = UpgradeCardManager()
    class Meta:
        proxy = True


class PilotCard2(Card):
    objects = PilotCardManager()

    class Meta:
        proxy = True


class Upgrade(Ability):
    cost = models.SmallIntegerField(default=0)
    repeat = models.BooleanField(default=False)
    type = models.CharField(max_length=3, choices=[c for c in SlotChoice.choices if c[0] != SlotChoice.PILOT.value])


    # there might be a better way to handle these.
    # for now, store the full list of icons a card adds with + as a seperator
    # eg "[Focus] + [Focus] [Link] [Evade]"
    adds = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        verbose_name = 'Upgrade Card'

    @property
    def add_list(self):
        return self.adds.split('+')


class PilotCard(Ability):
    initiative = models.PositiveSmallIntegerField(default=1)
    chassis = models.ForeignKey('Chassis', on_delete=models.CASCADE, related_name = 'pilot_card')
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=SlotChoice.choices, default=SlotChoice.PILOT)

    class Meta:
        verbose_name = 'Pilot Card'


class Attack(models.Model):
    ATTACK_REQS = (
        ('L', 'Lock'),
        ('F', 'Focus'),
        ('C', 'Calculate'),
        ('J', 'Force')
    )
    requires = models.CharField(max_length=1, choices=ATTACK_REQS, blank=True, null=True)
    arc = models.CharField(max_length=2, choices=ArcChoice.choices, default=ArcChoice.FRONT.value)
    dice = models.PositiveSmallIntegerField(default=3)
    range = models.CharField(max_length=3)
    ordnance = models.BooleanField(default=False)


class Dial(models.Model):
    chassis = models.OneToOneField('Chassis', on_delete=models.SET_NULL, null=True, related_name='dial')

    def __str__(self):
        return self.chassis.name or '--'

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
    dial = models.ForeignKey(Dial, on_delete=models.CASCADE, related_name='maneuvers')
    speed = models.PositiveSmallIntegerField()

    BEARING_TYPES = {
        'Straight': 'S',
        'Bank': 'B',
        'Turn': 'T',
        'K-Turn': 'KT',
        'Tallon Roll': 'TR',
        'Sloop': 'SL',
        'Reverse Bank': 'RB',
        'Stationary': 'SS',
        '--':'XX' # for use as a spacer
    }
    BEARING_CHOICES = [(v, k) for k, v in BEARING_TYPES.items()]
    bearing = models.CharField(max_length=3, choices=BEARING_CHOICES)

    DIRECTION_CHOICES = (
        ('L', 'Left'),
        ('R', 'Right')
    )
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES, null=True, blank=True )

    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_CHOICES, default='W')

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
        ordering = ['-speed', Case(
                When(bearing='XX', then=Value(1)),
                When(bearing='S', then=Value(2)),
                When(bearing='B', then=Value(3)),
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
    cloaking = models.BooleanField(default=False)

    css = models.CharField(max_length=80, null=True, blank=True)

    ability = models.OneToOneField(Upgrade,
                                   limit_choices_to={'type':SlotChoice.SHIP.value},
                                   null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    @property
    def css_name(self):
        return self.css if self.css else self.slug.replace('-', '')

    @property
    def arc1_css(self):
        return '{0}arc'.format(self.get_attack_arc_display().lower().replace(' ', ''))

    @property
    def arc2_css(self):
        return '{0}arc'.format(self.get_attack2_arc_display().lower().replace(' ', ''))

    class Meta:
        verbose_name_plural = 'Chassis'


class Slot(models.Model):
    chassis = models.ForeignKey(Chassis, related_name='slots', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=SlotChoice.choices)
    initiative = models.PositiveSmallIntegerField(default=1)

    @property
    def css_name(self):
        return self.get_type_display()
