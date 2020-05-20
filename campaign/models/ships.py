from django.db import models
from django.db.models import Case, When, Value

import re

from mptt.models import MPTTModel, TreeForeignKey

from xwtools.models import UPGRADE_CHOICES

# these models have been migrated to the xwtools app
# keeping them here until I'm sure it's safe to remove


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
    def dsort(self):
        return self.maneuvers\
            .annotate(dsort=Case(
                When(bearing='S', then=Value(2)),
                When(bearing='B', then=Value(3)),
                When(bearing='T', then=Value(4)),
                When(bearing='SL', then=Value(6)),
                When(bearing='KT', then=Value(8)),
                output_field=models.SmallIntegerField()) *
                Case(When(direction='L', then=Value(-1)),
                     default=Value(1),
                     output_field=models.SmallIntegerField())
             )\
    .order_by('-speed', 'dsort')

    @property
    def dial_width(self):
        speeds = {}
        for s in self.dsort.values_list('speed', flat=True):
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

    COLOR_CHOICES = (
        ('B', 'Blue'),
        ('W', 'White'),
        ('R', 'Red')
    )
    color = models.CharField(max_length=1, choices=COLOR_CHOICES, default='W')

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
        return {'B':'easy', 'R':'hard', 'W':''}[self.color]

    def __str__(self):
        return '{} {}{}{}'.format(self.speed,
                                   self.get_bearing_display(),
                                   ' ' + self.get_direction_display() if self.direction else '',
                                   '' if self.color == 'W' else ' ' + self.get_color_display())

    class Meta:
        ordering = ['-speed', Case(
                When(bearing='S', then=Value(1)),
                When(bearing='XX', then=Value(2)),
                When(bearing='B', then=Value(3)),
                When(bearing='T', then=Value(4)),
                When(bearing='SL', then=Value(6)),
                When(bearing='KT', then=Value(8)),
                output_field=models.SmallIntegerField()) *
                Case(When(direction='L', then=Value(-1)),
                     default=Value(1),
                     output_field=models.SmallIntegerField())]


class Ship(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=20, null=True)
    start_xp = models.PositiveSmallIntegerField(default=0)
    playable = models.BooleanField(default=True)
    dial = models.ForeignKey(Dial, on_delete=models.CASCADE)

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
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    threat = models.PositiveSmallIntegerField()
    cost = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)


class TreeSlot(MPTTModel):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    threat = models.PositiveSmallIntegerField()
    cost = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    type2 = models.CharField(max_length=3, choices=UPGRADE_CHOICES, null=True, blank=True, default=None)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return '{} {} - {} [{}]'.format(self.ship.name, self.threat, self.get_type_display(), self.cost)

    class Meta:
        ordering = ['threat', 'id', 'cost']
