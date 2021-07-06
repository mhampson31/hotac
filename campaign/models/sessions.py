from django.db import models
from django.db.models import Avg, Sum, Q
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .enemies import EnemyPilot, EnemyAbility
from .pilots import Pilot, PilotShip
from xwtools.models import Chassis
from math import floor

from .campaigns import User, Mission, Campaign, FlightGroup


class Session(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    pilots = models.ManyToManyField(Pilot, related_name='sessions', through='SessionPilot')
    enemies = models.ManyToManyField(EnemyPilot, through='SessionEnemy')
    date = models.DateField(null=True, blank=True)
    VICTORY = 'V'
    FAILURE = 'F'
    UNRESOLVED = 'U'
    OUTCOME_CHOICES = (
        (VICTORY, 'Victory'),
        (FAILURE, 'Failure'),
        (UNRESOLVED, 'Unresolved')
    )
    outcome = models.CharField(max_length=1, choices=OUTCOME_CHOICES, default='U')
    bonus_1_achieved = models.BooleanField(default=False)
    bonus_2_achieved = models.BooleanField(default=False)
    penalty_received = models.BooleanField(default=False)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('game:session', args=[str(self.id)])

    def __str__(self):
        return '{} {}'.format(self.mission.name, self.date)

    def add_pilots(self):
        for pilot in self.campaign.pilots.all():
            self.sessionpilot_set.create(pilot=pilot,
                                         ship=pilot.active_ship,
                                         initiative=pilot.initiative)

    def generate_enemies(self):
        from random import choice
        if self.outcome != 'U': # don't wipe info once the mission has been played
            return
        self.enemies.clear()
        fac = self.mission.enemy_faction
        enemy_list = EnemyPilot.objects.filter(faction=fac, random=True) \
                                       .exclude(Q(chassis_id=fac.default_ship.id)|Q(chassis_id__in=self.campaign.exclude_random.all()))
        #chassis_list = self.mission.enemy_faction.ships.exclude(Q(id=fac.default_ship.id)|Q(id__in=self.campaign.exclude_random.all()))
        for fg in self.mission.flight_groups.all():
            squad = fg.squad_members.filter(players__lte=self.pilots.count(), init__lte=self.group_init)
            p = 1 # just a counter to use in the callsigns

            # how many default enemies do we need to replace?
            replacements = squad.filter(action='R').count()

            # we handle replacements by collecting all the enemies in the flight group,
            # including the ones indicated as replacements. Then we go through the list
            # and add each one to the session, unless it's a default ship and we still
            # have replacements indicated
            for sq in squad:
                if replacements and sq.is_default:
                    replacements = replacements-1
                    pass
                else:
                    # if the FGSetup doesn't have a chassis, we select a non-default at random
                    if not sq.chassis:
                        new_enemy = choice(enemy_list.exclude(chassis=fac.default_ship))
                    else:
                        print(sq)
                        new_enemy = choice(enemy_list.filter(chassis=sq.chassis))
                    self.sessionenemy_set.create(flight_group=fg,
                                                 enemy=new_enemy,
                                                 callsign='%s %s' % (fg.name, p if p > 1 else 'Leader'),
                                                 level=self.group_init if sq.elite else EnemyAbility.Level.BASIC)
                    p = p + 1


    def debrief(self):
        """
        If the players have won the mission, update the mission deck.
        Other wrap-up can be included here.
        """
        if self.outcome == self.VICTORY and self.campaign.deck.filter(id=self.mission_id).exists():
            self.campaign.deck.remove(self.mission)
            try:
                next_mission = Mission.objects.get(rulebook=self.mission.rulebook,
                                                   story=self.mission.story,
                                                   sequence=self.mission.sequence+1)
                self.campaign.deck.add(next_mission)
            except Mission.DoesNotExist:
                pass
            self.save()

    @property
    def group_init(self):
        return min(6, floor(self.sessionpilot_set.aggregate(i=Avg('initiative'))['i']))

    @property
    def xp_pool(self):
        return sum([p.xp_pool for p in self.sessionpilot_set.all()])

    @property
    def xp_share(self):
        try:
            return floor(self.xp_pool/self.pilots.count())
        except ZeroDivisionError:
            return 0

    @property
    def xp_remainder(self):
        return self.xp_pool - (self.pilots.count() * self.xp_share)

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
    guards = models.SmallIntegerField(default=0)
    emplacements = models.SmallIntegerField(default=0)
    bonus = models.SmallIntegerField(default=0)
    penalty = models.SmallIntegerField(default=0)

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
        print('SessionPilot old chassis')
        return self.ship.chassis

    @property
    def xp_pool(self):
        return self.hits + self.assists + self.guards + self.emplacements + \
             sum([k.xp for k in self.kills.all()]) + \
             self.session.sessionenemy_set.filter(level__gte=2, killed_by__isnull=False).count() \
              - self.penalty

    @property
    def xp_earned(self):
        xp = self.session.xp_share if self.session.campaign.pool_xp else self.xp_pool
        xp = xp + self.bonus
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
        return 1 + self.enemy.non_default_ship + self.enemy.large_ship
