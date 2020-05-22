from django.db import models
from django.db.models import Case, When, Value

import re

SLOT_TYPES = {
    'Talent':'0',
    'Astromech':'1',
    'Cannon':'2',
    'Config':'3',
    'Crew':'4',
    'Device':'5',
    'Pilot':'6', # takes talents, force, and pilot upgrades
    'Gunner':'7',
    'Illicit':'8',
    'Missile':'9',
    'Modification':'10',
    'Sensor':'11',
    'Relay':'12',
    'Tech':'13',
    'Title':'14',
    'Torpedo':'15',
    'Turret':'16'
}
SLOT_CHOICES = [(v, k) for k, v in SLOT_TYPES.items()]

UPGRADE_TYPES = {
    'AST':('Astromech', SLOT_TYPES['Astromech']),
    'CNN':('Cannon', SLOT_TYPES['Cannon']),
    'CNF': ('Configuration', SLOT_TYPES['Config']),
    'CRW': ('Crew', SLOT_TYPES['Crew']),
    'DVC': ('Device', SLOT_TYPES['Device']),
    'FRC': ('Force Power', SLOT_TYPES['Pilot']),
    'GNR': ('Gunner', SLOT_TYPES['Gunner']),
    'ILC': ('Illicit', SLOT_TYPES['Illicit']),
    'MSL': ('Missile', SLOT_TYPES['Missile']),
    'MOD': ('Modification', SLOT_TYPES['Modification']),
    'SNS':('Sensor', SLOT_TYPES['Sensor']),
    'TAC': ('Tactical Relay', SLOT_TYPES['Relay']),
    'TLN': ('Talent', SLOT_TYPES['Pilot']),
    'TCH': ('Tech', SLOT_TYPES['Tech']),
    'TTL': ('Title', SLOT_TYPES['Title']),
    'TRP': ('Torpedo', SLOT_TYPES['Torpedo']),
    'TRT': ('Turret', SLOT_TYPES['Turret']),
    'SHP': ('Ship', 0),
    'PLT': ('Pilot', SLOT_TYPES['Pilot']),
    'THR': ('Initiative', 0),
    'FCH': ('Force Charge', 0),
    'CHR': ('Charge', 0),
    'WLD': ('Wildcard', 0)
}
UPGRADE_CHOICES = [(k, v[0]) for k, v in UPGRADE_TYPES.items()]

DIFFICULTY_CHOICES = (
        ('B', 'Blue'),
        ('W', 'White'),
        ('R', 'Red'),
        ('P', 'Purple')
)


class Upgrade(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    type2 = models.CharField(max_length=3, choices=UPGRADE_CHOICES, null=True, blank=True, default=None)
    cost = models.PositiveSmallIntegerField()
    charges = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['type', '-type2', 'name']


class Dial(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

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
            return self.dial.dialmaneuver_set.get(speed=self.speed, move=self.bearing, direction=new_direction)

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
    dial = models.ForeignKey(Dial, on_delete=models.CASCADE)

    ARC_CHOICES = (
        ('F', 'Front'),
        ('R', 'Rear')
    )
    attack = models.PositiveSmallIntegerField(default=0)
    attack_arc = models.CharField(max_length=2, choices=ARC_CHOICES, default='F')
    attack2 = models.PositiveSmallIntegerField(default=0)
    attack2_arc = models.CharField(max_length=2, choices=ARC_CHOICES, null=True, blank=True)
    agility = models.PositiveSmallIntegerField(default=0)
    hull = models.PositiveSmallIntegerField(default=0)
    shields = models.PositiveSmallIntegerField(default=0)

    FACTION_CHOICES = (
        ('RA', 'Rebel Alliance'),
        ('GE', 'Galactic Empire'),
        ('SV', 'Scum and Villainy'),
        ('RS', 'Resistance'),
        ('FO', 'First Order'),
        ('GR', 'Republic'),
        ('SE', 'Seperatist')
    )
    faction = models.CharField(max_length=2, choices=FACTION_CHOICES, default='RA')

    def __str__(self):
        return self.name

    @property
    def css_name(self):
        return self.dial.css_name


class Slot(models.Model):
    chassis = models.ForeignKey(Chassis, related_name='slots', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=SLOT_CHOICES)
    initiative = models.PositiveSmallIntegerField(default=1)

    @property
    def css_name(self):
        return self.get_type_display()
