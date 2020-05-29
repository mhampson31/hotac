from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _

from math import floor

from .campaigns import User, Campaign, Mission, Event, EnemyPilot, EnemyAbility, FlightGroup
from xwtools.models import Chassis, Upgrade


class Game(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=30)
    victory = models.PositiveSmallIntegerField()
    ship_initiative = models.BooleanField(default=False)
    pool_xp = models.BooleanField(default=False)
    gm = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='game_gm')
    players = models.ManyToManyField(User)


    def __str__(self):
        return self.description

    @property
    def xp_share(self):
        pilots = 0
        xp = 0
        for s in self.session_set.all():
            pilots = pilots + s.pilots.count()
            xp = xp + s.xp_total
        return floor(xp/pilots)


class Pilot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True)
    callsign = models.CharField(max_length=30)
    upgrades = models.ManyToManyField(Upgrade)
    initiative = models.PositiveSmallIntegerField(default=2)

    PATH_CHOICES = (
        ('F', 'Force User'),
        ('A', 'Ace')
    )
    path = models.CharField(max_length=1, choices=PATH_CHOICES, default='A')

    def __str__(self):
        return '{} ({})'.format(self.callsign, self.user)

    @property
    def total_xp(self):
        xp = self.game.campaign.squadron_set.get(chassis=self.pilotship_set.first().chassis).start_xp + \
            (self.achievement_set.filter(event__team=False).aggregate(xp=Sum('event__xp'))['xp'] or 0)
        if self.game.pool_xp:
            return xp + self.game.xp_share * self.session_set.count()
        else:
            return xp + sum([a.xp for a in self.achievement_set.filter(event__team=True)])


class PilotShip(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE, null=True)
    initiative = models.PositiveSmallIntegerField(default=2)
    hull_upgrades = models.PositiveSmallIntegerField(default=0)
    shield_upgrades = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.pilot.callsign + "\'s " + self.chassis.name

    @property
    def slots(self):
        i = self.initiative if self.pilot.game.ship_initiative else self.pilot.initiative
        slot_list = [s.get_type_display() for s in self.chassis.slots.all()]
        path_slot = {'A':'Pilot', 'F':'Force Power'}[self.pilot.path]

        if i >= 3:
            slot_list.append(path_slot)
        if i >= 4:
            slot_list.append('Modification')
        if i >= 5:
            prog = self.pilot.game.campaign.squadron_set.get(id=self.chassis.id).progression
            slot_list.append({'d':path_slot,
                              'h':'Sensor'}[prog])
        if i == 6:
            slot_list.extend((path_slot, 'Modification'))
        slot_list.sort()
        return slot_list



class Session(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    pilots = models.ManyToManyField(Pilot)
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

    @property
    def group_init(self):
        return min(6, floor(self.pilots.aggregate(i=Avg('initiative'))['i']))

    @property
    def xp_total(self):
        a = self.achievement_set.filter(event__team=True)
        return a.aggregate(total=(models.Sum('threat') or 0) + (models.Sum('event__xp') or 0))['total'] or 0

    @property
    def xp_earned(self):
        return floor(self.xp_total/self.pilots.count())

    @property
    def xp_remainder(self):
        return self.xp_total - (self.pilots.count() * self.xp_earned)


class SessionEnemy(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    enemy = models.ForeignKey(EnemyPilot, on_delete=models.CASCADE)
    flight_group = models.ForeignKey(FlightGroup, on_delete=models.CASCADE)
    level = models.SmallIntegerField(choices=EnemyAbility.Level.choices, default=1)

    def __str__(self):
        if self.elite:
            return '{} - Elite {}'.format(self.enemy.chassis.name, self.level)
        else:
            return self.enemy.chassis.name

    @property
    def elite(self):
        return self.level > 1

    @property
    def abilities(self):
        return self.enemy.abilities.filter(level__lte=self.level)



"""
class SessionPilot(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    ship = models.ForeignKey(PilotShip, on_delete=models.CASCADE)
    initiative = models.SmallIntegerField(null=True)

    class StatusChoice(models.TextChoices):
        NOT_FLOWN = 'P', _('Not Flown')
        VICTORY = 'V', _('Victory')
        EJECTED = 'F', _('Ejected - Half XP')
        NO_XP = 'N', _('Ejected - No XP')
        LOST_UPGRADE = 'H', _('Ejected - Lost Upgrade')
        LOST_PILOT = 'C', _('Ejected - Lost Talent')
        KIA = 'K', _('Killed In Action')

    status = models.CharField(max_length=1, choices=StatusChoice.choices, default=StatusChoice.NOT_FLOWN)
"""


class Achievement(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, default=1)
    turn = models.PositiveSmallIntegerField()
    threat = models.SmallIntegerField(null=True, blank=True)

    @property
    def xp(self):
        return (self.event.xp or 0) + (self.threat or 0)
