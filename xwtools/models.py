from django.db import models
from django.db.models import Case, When, Value
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
    ILLICIT = 'ILC', _('Illicit`')
    MISSILE = 'MSL', _('Missile')
    MODIFICATION = 'MOD', _('Modification')
    SENSOR = 'SNS', _('Sensor')
    RELAY = 'TAC', _('Tactical Relay')
    TECH = 'TCH', _('Tech')
    TORPEDO = 'TRP', _('Torpedo')
    TITLE = 'TTL', _('Title')
    TURRET = 'TRT', _('Turret')
    SHIP = 'SHP', _('Ship')


class Ability(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255, null=True, blank=True)
    ai_description = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=3, choices=SlotChoice.choices)
    type2 = models.CharField(max_length=3, choices=SlotChoice.choices, null=True, blank=True, default=None)
    charges = models.PositiveSmallIntegerField(null=True, blank=True)
    force = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['type', '-type2', 'name']


DIFFICULTY_CHOICES = (
        ('B', 'Blue'),
        ('W', 'White'),
        ('R', 'Red'),
        ('P', 'Purple')
)

class Faction(models.Model):
    name = models.CharField(max_length=20)
    ships = models.ManyToManyField('Chassis')
    default_ship = models.OneToOneField('Chassis', on_delete=models.CASCADE, related_name='default_for')

    def __str__(self):
        return self.name


class Upgrade(Ability):
    cost = models.SmallIntegerField(default=0)


class Dial(models.Model):
    #chassis = models.OneToOneField(Chassis, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return self.name or '--'

    @property
    def css_name(self):
        return re.sub(r'[^\w\d]', '', self.name.lower())

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
    slug = models.SlugField(max_length=20, null=True)

    dial = models.OneToOneField(Dial, on_delete=models.SET_NULL, null=True, related_name='chassis')

    ARC_CHOICES = (
        ('F', 'Front'),
        ('R', 'Rear')
    )

    class SizeChoices(models.TextChoices):
        SMALL = 'S', _('Small')
        MEDIUM = 'M', _('Medium')
        LARGE = 'L', _('Large')
        HUGE = 'H', _('Huge')

    size = models.CharField(max_length=1, choices=SizeChoices.choices, default=SizeChoices.SMALL)
    attack = models.PositiveSmallIntegerField(default=0)
    attack_arc = models.CharField(max_length=2, choices=ARC_CHOICES, default='F')
    attack2 = models.PositiveSmallIntegerField(default=0)
    attack2_arc = models.CharField(max_length=2, choices=ARC_CHOICES, null=True, blank=True)
    agility = models.PositiveSmallIntegerField(default=0)
    hull = models.PositiveSmallIntegerField(default=0)
    shields = models.PositiveSmallIntegerField(default=0)
    hyperdrive = models.BooleanField(default=True)
    cloaking = models.BooleanField(default=False)

    css = models.CharField(max_length=80, null=True, blank=True)

    ability = models.OneToOneField(Upgrade,
                                   limit_choices_to={'type':SlotChoice.SHIP.value},
                                   null=True,
                                   blank=True,
                                   on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    @property
    def css_name(self):
        return self.css if self.css else self.slug.replace('-', '')

    class Meta:
        verbose_name_plural = 'Chassis'


class Slot(models.Model):
    chassis = models.ForeignKey(Chassis, related_name='slots', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=SlotChoice.choices)
    initiative = models.PositiveSmallIntegerField(default=1)

    @property
    def css_name(self):
        return self.get_type_display()

class Pilot(Ability):
    initiative = models.PositiveSmallIntegerField(default=1)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
