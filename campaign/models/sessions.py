from django.db import models
from django.db.models import Avg, Sum
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from math import floor

from .campaigns import User, Mission, Event, Campaign, FlightGroup
from .enemies import EnemyPilot, EnemyAbility
from .pilots import Pilot, PilotShip
from xwtools.models import Chassis, Upgrade


class Session(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    pilots = models.ManyToManyField(Pilot, related_name='sessions', through='SessionPilot')
    enemies = models.ManyToManyField(EnemyPilot, through='SessionEnemy')
    date = models.DateField()
    VICTORY = 'V'
    FAILURE = 'F'
    UNRESOLVED = 'U'
    OUTCOME_CHOICES = (
        (VICTORY, 'Victory'),
        (FAILURE, 'Failure'),
        (UNRESOLVED, 'Unresolved')
    )
    outcome = models.CharField(max_length=1, choices=OUTCOME_CHOICES, default='U')

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('session', args=[str(self.id)])

    def __str__(self):
        return '{} {}'.format(self.mission.name, self.date)

    def generate_enemies(self):
        from random import choice
        self.enemies.clear()
        fac = self.mission.enemy_faction
        enemy_list = EnemyPilot.objects.filter(faction=fac)
        chassis_list = self.mission.enemy_faction.ships.exclude(id=fac.default_ship.id)
        for fg in self.mission.flight_groups.all():
            squad = fg.squad_members.filter(players__lte=self.pilots.count(), init__lte=self.group_init)

            # how many default enemies do we need to replace?
            r = squad.filter(action='R').count()
            for sq in squad:
                if r and sq.is_default:
                    r = r-1
                    pass
                else:
                    if not sq.chassis:
                        new_enemy = choice(enemy_list.exclude(chassis=fac.default_ship))
                    else:
                        new_enemy = choice(enemy_list.filter(chassis=sq.chassis))
                    self.sessionenemy_set.create(flight_group=fg,
                                                 enemy=new_enemy,
                                                 level=self.group_init if sq.elite else EnemyAbility.Level.BASIC)
        current_fg = ''
        p = 1
        for se in self.sessionenemy_set.all():
            if current_fg != se.flight_group.name:
                current_fg == se.flight_group.namespace
                p = 1
            se.callsign = '%s %s' % (se.flight_group.name, p if p > 1 else 'Leader')
            se.save()
            p = p + 1

    @property
    def group_init(self):
        return min(6, floor(self.sessionpilot_set.aggregate(i=Avg('initiative'))['i']))

    @property
    def xp_total(self):
        return sum([p.xp_earned for p in self.sessionpilot_set.all()])

    @property
    def xp_earned(self):
        return floor(self.xp_total/self.pilots.count())

    @property
    def xp_remainder(self):
        return self.xp_total - (self.pilots.count() * self.xp_earned)

    @property
    def team_xp(self):
        return 0


class SessionPilot(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    ship = models.ForeignKey(PilotShip, on_delete=models.CASCADE)
    initiative = models.PositiveSmallIntegerField(default=2) #capturing init at game time
    hits = models.SmallIntegerField(default=0)
    assists = models.SmallIntegerField(default=0)
    guardians = models.SmallIntegerField(default=0)

    class StatusChoice(models.TextChoices):
        NOT_FLOWN = 'P', _('Not Flown')
        VICTORY = 'V', _('Victory')
        EJECTED = 'F', _('Ejected - Half XP')
        NO_XP = 'N', _('Ejected - No XP')
        LOST_UPGRADE = 'H', _('Ejected - Lost Upgrade')
        LOST_PILOT = 'C', _('Ejected - Lost Talent')
        KIA = 'K', _('Killed In Action')

    status = models.CharField(max_length=1, choices=StatusChoice.choices, default=StatusChoice.NOT_FLOWN)

    def __str__(self):
        return self.pilot.callsign

    @property
    def chassis(self):
        return self.ship.chassis

    @property
    def xp_earned(self):
        xp = self.hits + self.assists + self.guardians + sum([k.xp for k in self.kills.all()])
        if self.status == self.StatusChoice.EJECTED:
            return floor(xp/2)
        elif self.status in [self.StatusChoice.NO_XP, self.StatusChoice.KIA, self.StatusChoice.NOT_FLOWN]:
            return 0
        else:
            return xp


class SessionEnemy(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    enemy = models.ForeignKey(EnemyPilot, on_delete=models.CASCADE)
    flight_group = models.ForeignKey(FlightGroup, on_delete=models.CASCADE)
    callsign = models.CharField(max_length=30, default='')
    level = models.SmallIntegerField(choices=EnemyAbility.Level.choices, default=1)
    killed_by = models.ForeignKey(SessionPilot, on_delete=models.SET_NULL, blank=True, null=True, related_name='kills')

    def old__str__(self):
        base = '[{}] {}'.format(self.flight_group.name, self.enemy.chassis.name)
        if self.elite:
            base =  '{} - Elite {}'.format(base, self.level)
        return base

    def __str__(self):
        return self.callsign

    class Meta:
        ordering = ['flight_group', '-level']

    @property
    def pilot(self):
        return self.enemy

    @property
    def chassis(self):
        return self.enemy.chassis

    @property
    def elite(self):
        return self.level > 1

    @property
    def initiative(self):
        if self.elite:
            return self.level + 1
        else:
            return 1

    @property
    def abilities(self):
        return self.enemy.abilities.filter(level__lte=self.level)

    @property
    def xp(self):
        return 1 + self.elite + self.enemy.non_default_ship + self.enemy.large_ship


class Achievement(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='achievements')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, default=1)
    turn = models.PositiveSmallIntegerField()
    target = models.OneToOneField(SessionEnemy, on_delete=models.SET_NULL, null=True, blank=True)

    threat = models.SmallIntegerField(null=True, blank=True)
