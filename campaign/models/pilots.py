from django.db import models
from django.urls import reverse
from django.db.models import Sum, Q, F
from django.db.models.functions import Coalesce, Least

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from xwtools.models import Chassis, SlotChoice, Card, PilotCard
from .campaigns import User, Campaign, UpgradeLogic


class UStatusChoice(models.TextChoices):
    EQUIPPED = 'E', 'Equipped'
    UNEQUIPPED = 'U', 'Unequipped'
    LOST = 'X', 'Lost'


class Pilot(models.Model):
    """
    This model represents a player's character pilot, not a pilot card.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, related_name='pilots')
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
        return reverse('game:pilot', kwargs={'pk': self.pk})

    @property
    def total_xp(self):
        base = self.pilotship_set.first().game_info.xp_value
        if self.campaign.pool_xp:
            earned = sum([s.xp_share for s in self.sessions.all()] + \
                         [s.bonus for s in self.sessionpilot_set.all()])
        else:
            earned = sum([s.xp_earned for s in self.sessionpilot_set.all()])
        return base + earned

    @property
    def spent_xp(self):
        return self.spent_ships + self.spent_upgrades + self.spent_initiative

    @property
    def spent_ships(self):
        return (self.ships.count() - 1) * F('campaign__rulebook__ship_cost')

    @property
    def spent_upgrades(self):
        return sum([u.cost for u in self.upgrades.all()])

    @property
    def spent_initiative(self):
        levels = range(self.campaign.rulebook.start_init, self.initiative)
        if self.campaign.rulebook.initiative_sq:
            return sum([(l+1)^2 for l in levels])
        else:
            return sum([(l+1)*self.campaign.rulebook.initiative_cost for l in levels])

    @property
    def active_ship(self):
        # grab the active ship. If there's somehow multiple, grab the newest
        return self.pilotship_set.filter(active=True).last()

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
        for ss in self.active_ship.chassis.slots.all():
            slot_list.append(next(s2 for s2 in SlotChoice if s2.value == ss.type))

        # maybe change Pilot.path to use SlotChoice...
        #path_slot = {'A':SlotChoice.PILOT, 'F':SlotChoice.FORCE}[self.path]
        path_slot = SlotChoice.PILOT

        if self.initiative >= 3:
            slot_list.append(path_slot)
        if self.initiative >= 4:
            slot_list.append(SlotChoice.MODIFICATION)
        if self.initiative >= 5:
            #prog = self.campaign.rulebook.playableship_set.get(id=self.active_ship.id).progression
            prog = self.active_ship.game_info.progression
            slot_list.append({'d':path_slot,
                              'h':SlotChoice.SENSOR}[prog])
        if self.initiative == 6:
            slot_list.append(path_slot)
            slot_list.append(SlotChoice.MODIFICATION)
        slot_list.sort()
        return slot_list

    @property
    def available_upgrades(self):
        slots = [s.value for s in self.slots]

        if SlotChoice.PILOT in slots:
            slots.append(SlotChoice.FORCE.value)
            slots.append(SlotChoice.TALENT.value)

        # The upgrade list queryset takes some assembly.
        # First, grab all the CampaignUpgrades that the players has slots for
        # (Those missing descriptions are assumed to be AI-only abilities)

        # Next, exclude any the player already has, unless they're marked as repeatable

        # Then exclude any Pilot upgrades belonging to a different faction

        # Finally, put everything in order

        upgrade_query = Card.objects \
            .filter(type__in=slots, player_use=True, initiative__lte=self.initiative) \
            .exclude(id__in=self.upgrades.filter(card__repeat=False).values_list('card__id', flat=True)) \
            .exclude(Q(type=SlotChoice.PILOT), \
                    ~Q(id__in=Card.objects.filter(faction=self.campaign.rulebook.faction).values_list('id', flat=True))) \
            .select_related('chassis', 'faction') \
            .order_by('type', 'name')

        return upgrade_query

    @property
    def force_charges(self):
        """
        A pilot's Force charges equals the count of Force upgrades plus the Force charges
        on other cards, to a max of 3.
        HotAC rules as written don't seem to account for cards like Ezra (gunner)
        but we're counting them here.
        """
        return self.upgrades.filter(Q(status=UStatusChoice.EQUIPPED), \
                                    Q(card__type='FRC')|Q(card__force=True)) \
                            .aggregate(fc=Least(Sum(Coalesce('card__charges', 1)), 3))['fc']



class PilotShip(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE, null=True, related_name='pilot_ship')
    active = models.BooleanField(default = True)
    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        indexes = [
        models.Index(fields=['active',])
        ]

    def __str__(self):
        if self.name:
            return "{}'s {} {}".format(self.pilot.callsign, self.chassis.name, self.name)
        else:
            return "{}'s {}".format(self.pilot.callsign, self.chassis.name)

    @property
    def game_info(self):
        return self.pilot.campaign.rulebook.playableship_set.get(chassis=self.chassis)


class PilotUpgrade(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE, related_name='upgrades')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=1, choices=UStatusChoice.choices, default='E')

    @property
    def cost(self):
        return self.card.campaign_cost(self.pilot.campaign.rulebook.upgrade_logic)

    def __str__(self):
        return str(self.card)

    class Meta:
        ordering = ['card__type', 'status']
