from django.db import models

from xwtools.models import Chassis, Faction, SizeChoice, Card

class EnemyPilot(models.Model):
    chassis = models.ForeignKey(Chassis, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    upgrades = models.ManyToManyField(Card, through='EnemyAbility')
    name_override = models.CharField(max_length=35, blank=True, null=True)
    random = models.BooleanField(default=True)

    def __str__(self):
        if self.chassis == self.faction.default_ship:
            return self.chassis.name
        else:
            name = self.name_override or self.in5
            return '{} - {}'.format(self.chassis.name, name)

    def ability_list(self, lvl=1):
        return '/'.join(self.abilities.filter(level__lte=lvl).values_list('card__name', flat=True))

    @property
    def basic(self):
        return '/'.join(self.abilities.filter(level=1).values_list('card__name', flat=True))

    @property
    def elite(self):
        return '/'.join(self.abilities.filter(level=2).values_list('card__name', flat=True))

    @property
    def in3(self):
        return '/'.join(self.abilities.filter(level=3).values_list('card__name', flat=True))

    @property
    def in4(self):
        return '/'.join(self.abilities.filter(level=4).values_list('card__name', flat=True))

    @property
    def in5(self):
        return '/'.join(self.abilities.filter(level=5).values_list('card__name', flat=True))

    @property
    def non_default_ship(self):
        return self.chassis != self.faction.default_ship

    @property
    def large_ship(self):
        return self.chassis.size in (SizeChoice.LARGE, SizeChoice.HUGE)


class EnemyAbility(models.Model):
    pilot = models.ForeignKey(EnemyPilot, on_delete=models.CASCADE, related_name='abilities')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, limit_choices_to={'ai_description__isnull':False})

    class Level(models.IntegerChoices):
        BASIC = 1
        ELITE = 2
        IN_3 = 3
        IN_4 = 4
        IN_5 = 5

    level = models.SmallIntegerField(choices=Level.choices, default=1)

    def __str__(self):
        return self.card.name
