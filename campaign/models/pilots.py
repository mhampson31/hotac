from django.db import models
from django.urls import reverse
from django.db.models import Sum

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from xwtools.models import Chassis, Upgrade, SlotChoice
from .campaigns import User, Campaign, Game, GameUpgrade


class Pilot(models.Model):
    """
    This model represents a player's character pilot, not a pilot card.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True)
    ships = models.ManyToManyField(Chassis, through='PilotShip', related_name='pilot_character')
    callsign = models.CharField(max_length=30)
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
        return sum([self.game.campaign.upgrade_cost(u.upgrade) * u.copies
                    for u in self.upgrades.filter(upgrade__cost__gt=0)
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
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE, null=True, related_name='pilot_ship')
    initiative = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return self.pilot.callsign + "\'s " + self.chassis.name

    @property
    def campaign_info(self):
        return self.pilot.game.campaign.playership_set.get(chassis=self.chassis)



class PilotUpgrade(models.Model):
    class UStatusChoice(models.TextChoices):
        EQUIPPED = 'E', 'Equipped'
        UNEQUIPPED = 'U', 'Unequipped'
        LOST = 'X', 'Lost'

    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE, related_name='upgrades')
    upgrade = models.ForeignKey(GameUpgrade, on_delete=models.CASCADE)

    copies = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=1, choices=UStatusChoice.choices, default='E')

    @property
    def cost(self):
        return self.pilot.game.campaign.upgrade_cost(self.upgrade) * self.copies

    @property
    def charges(self):
        if self.upgrade.charges:
            return self.upgrade.charges + self.copies - 1
        else:
            return None

    def __str__(self):
        s = str(self.upgrade)
        if self.copies > 1:
            if self.upgrade.type == SlotChoice.MODIFICATION:
                s = '{} x{}'.format(s, self.copies)
            else:
                # for ordinance things, copies are the extra charges granted
                s = '{} +{}'.format(s, self.copies-1)
        return s

    class Meta:
        ordering = ['upgrade__type', 'status']
