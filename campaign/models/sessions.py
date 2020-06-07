from django.db import models
from django.db.models import Avg, Sum
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from math import floor

from .campaigns import User, Campaign, Mission, Event, EnemyPilot, EnemyAbility, FlightGroup
from xwtools.models import Chassis, Upgrade, SlotChoice


class Game(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True)
    gm = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='game_gm')
    players = models.ManyToManyField(User)
    description = models.CharField(max_length=30)

    victory = models.PositiveSmallIntegerField()
    ship_initiative = models.BooleanField(default=False)
    pool_xp = models.BooleanField(default=False)


    def __str__(self):
        return self.description

    @property
    def xp_share(self):
        """
        Used when XP pooling is chosen for the game.
        Calculates total xp across all sessions and total number of pilot shares.
        Each mission flown earns a pilot one share in the group's total xp.
        """
        pilots = 0
        xp = 0
        for s in self.session_set.all():
            pilots = pilots + s.pilots.count()
            xp = xp + s.xp_total
        return floor(xp/pilots)


class Pilot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True)
    ships = models.ManyToManyField(Chassis, through='PilotShip')
    callsign = models.CharField(max_length=30)
    upgrades = models.ManyToManyField(Upgrade, through='PilotUpgrade')
    initiative = models.PositiveSmallIntegerField(default=2)

    PATH_CHOICES = (
        ('F', 'Force User'),
        ('A', 'Ace')
    )
    path = models.CharField(max_length=1, choices=PATH_CHOICES, default='A')

    def __str__(self):
        return '{} ({})'.format(self.callsign, self.user)


    def get_absolute_url(self):
        return reverse('pilot', kwargs={'pk': self.pk})

    @property
    def total_xp(self):
        #ship_xp
        #achievement_xp =
        #self.game.campaign.ships.get(id=self.pilotship_set.first().chassis.id).start_xp
        base = self.pilotship_set.first().campaign_info.xp_value

        if self.game.pool_xp:
            earned = self.game.xp_share * self.sessions.count()
        else:
            earned = sum([s.pilot_xp(self) for s in self.sessions.all()])

        return base + earned

    @property
    def spent_xp(self):
        return self.spent_ships + self.spent_upgrades + self.spent_initiative

    @property
    def spent_ships(self):
        return (self.ships.count() - 1) * self.game.campaign.ship_cost

    @property
    def spent_upgrades(self):
        return sum([self.game.campaign.upgrade_cost(u)
                    for u in self.upgrades.filter(cost__gt=0)
                    ])

    @property
    def spent_initiative(self):
        # the amount spent on initiative depends on whether the cost is squared
        # or multiplied. For each init value between the start and current init
        # (i+1 because of range()'s return values), raise it to the power of 1
        # plus the numeric value of the initiative_sq setting (so **1 for False,
        # **2 for True). Sum all these values, and multiply them by the init
        # multipler.
        return sum([
                    (i+1) ** (1 + self.game.campaign.initiative_sq)
                    for i in range(self.game.campaign.start_init, self.initiative)]) \
               * self.game.campaign.initiative_cost


    @property
    def active_ship(self):
        return self.ships.last()

    @property
    def starter_ship(self):
        return self.ships.first()

    @property
    def slots(self):
        """
        Compile the list of slots available to a player, according to their
        active ship's defaults, their initiative, their chosen progression path,
        and their ship's progression path
        """
        slot_list = []
        # get ship slot choices
        for ss in self.active_ship.slots.all():
            slot_list.append(next(s2 for s2 in SlotChoice if s2.value == ss.type))

        # maybe change Pilot.path to use SlotChoice...
        path_slot = {'A':SlotChoice.PILOT, 'F':SlotChoice.FORCE}[self.path]

        if self.initiative >= 3:
            slot_list.append(path_slot)
        if self.initiative >= 4:
            slot_list.append(SlotChoice.MODIFICATION)
        if self.initiative >= 5:
            prog = self.game.campaign.playership_set.get(id=self.active_ship.id).progression
            slot_list.append({'d':path_slot,
                              'h':SlotChoice.SENSOR}[prog])
        if self.initiative == 6:
            slot_list.append(path_slot)
            slot_list.append(SlotChoice.MODIFICATION)
        slot_list.sort()
        return slot_list


class PilotShip(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE, null=True)
    initiative = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return self.pilot.callsign + "\'s " + self.chassis.name

    @property
    def campaign_info(self):
        return self.pilot.game.campaign.playership_set.get(chassis=self.chassis)

    @property
    def slots(self):
        print('Deprecated: PilotShip.slots()')
        return self.pilot.slots


class PilotUpgrade(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    upgrade = models.ForeignKey(Upgrade, on_delete=models.CASCADE)
    copies = models.PositiveSmallIntegerField(default=1)
    lost = models.BooleanField(default=False)


class Session(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    pilots = models.ManyToManyField(Pilot, related_name='sessions')
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

    @property
    def group_init(self):
        return min(6, floor(self.pilots.aggregate(i=Avg('initiative'))['i']))

    @property
    def xp_total(self):
        return sum([a.xp for a in self.achievements.all()]) + (self.team_xp * self.pilots.count())
        #a = self.achievement_set.all()
        #return a.aggregate(total=(models.Sum('threat') or 0) + (models.Sum('event__xp') or 0))['total'] or 0

    @property
    def xp_earned(self):
        return floor(self.xp_total/self.pilots.count())

    @property
    def xp_remainder(self):
        return self.xp_total - (self.pilots.count() * self.xp_earned)

    @property
    def team_xp(self):
        return self.achievements.filter(target__level__gt=1).count()

    def pilot_xp(self, p):
        return sum([a.xp for a in self.achievements.filter(pilot=p)]) + self.team_xp


class SessionEnemy(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    enemy = models.ForeignKey(EnemyPilot, on_delete=models.CASCADE)
    flight_group = models.ForeignKey(FlightGroup, on_delete=models.CASCADE)
    level = models.SmallIntegerField(choices=EnemyAbility.Level.choices, default=1)

    def __str__(self):
        base = '[{}] {}'.format(self.flight_group.name, self.enemy.chassis.name)
        if self.elite:
            base =  '{} - Elite {}'.format(base, self.level)
        return base

    class Meta:
        ordering = ['flight_group', '-level']

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
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='achievements')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, default=1)
    turn = models.PositiveSmallIntegerField()
    target = models.OneToOneField(SessionEnemy, on_delete=models.SET_NULL, null=True, blank=True)

    threat = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        if self.target:
            return '{} {}'.format(self.event.long_desc, self.target.enemy.chassis.name)
        else:
            return '{}'.format(self.event.long_desc)

    @property
    def xp(self):
        xp = 1
        if self.target:
            if self.target.enemy.chassis.size == Chassis.SizeChoices.LARGE:
                xp = xp + 1
            if self.target.enemy.chassis != self.session.mission.enemy_faction.default_ship:
                xp = xp + 1
        return xp

    @property
    def team_xp(self):
        if self.target and self.target.elite:
            return 1

        #return (self.event.xp or 0) + (self.threat or 0)
