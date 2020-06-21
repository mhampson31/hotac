from django.db import models

from .campaigns import Rulebook
from xwtools.models import Dial, DialManeuver

from smart_selects.db_fields import ChainedForeignKey


class AI(models.Model):
    rulebook = models.ForeignKey(Rulebook, on_delete=models.CASCADE)
    dial = models.ForeignKey(Dial, on_delete=models.CASCADE)
    flee = models.PositiveSmallIntegerField(default=0)

    VERSION_CHOICES = (
        ('f7', 'FGA 0.7'),
    )
    version = models.CharField(max_length=3, choices=VERSION_CHOICES, default='f7')

    def __str__(self):
        return '{} AI'.format(self.dial.chassis.name)


    def mirror(self):
        """
        A helper function that makes left-sided copies of all the right-side maneuver tables
        :return: Nothing, saves new objects directly
        """

        for mv in self.aimaneuver_set.filter(arc__in=('FR', 'RF', 'RA', 'AR')):
            new_arc = mv.arc.replace('R', 'L')
            if not self.aimaneuver_set.filter(arc=new_arc, range=mv.range).exists():
                mv.pk = None
                mv.arc = new_arc
                mv.roll_1 = mv.roll_1.find_mirror()
                mv.roll_2 = mv.roll_2.find_mirror()
                mv.roll_3 = mv.roll_3.find_mirror()
                mv.roll_4 = mv.roll_4.find_mirror()
                mv.roll_5 = mv.roll_5.find_mirror()
                mv.roll_6 = mv.roll_6.find_mirror()
                mv.save()

    class Meta:
        verbose_name_plural = 'AI'


class AIManeuver(models.Model):
    RANGE_CHOICES = (
        ('1', 'R1/R2 Closing'),
        ('2', 'R3/R2 Fleeing'),
        ('3', 'R4+'),
        ('4', 'Stressed'),
        ('5', 'Fleeing')
    )

    AI_ARC_CHOICES = (
        ('BE', 'Bullseye'),
        ('FR', 'Front (Right)'),
        ('RF', 'Right (Front)'),
        ('RA', 'Right (Rear)'),
        ('AR', 'Rear (Right)'),
        ('FL', 'Front (Left)'),
        ('LF', 'Left (Front)'),
        ('LA', 'Left (Rear)'),
        ('AL', 'Rear (Left)')
    )

    ai = models.ForeignKey(AI, on_delete=models.CASCADE)
    arc = models.CharField(max_length=2, choices=AI_ARC_CHOICES)
    range = models.CharField(max_length=1, choices=RANGE_CHOICES)

    # these are denormalized mainly to make data entry easier, so we don't need
    # to have an AI, AIManeuver, and a theoretical AIManeuverRoll model all on one admin page
    roll_1 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_1')
    roll_2 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_2')
    roll_3 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_3')
    roll_4 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_4')
    roll_5 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_5')
    roll_6 = ChainedForeignKey(DialManeuver, chained_field='ai', chained_model_field='dial', related_name='roll_6')

    def get_maneuvers(self): return True

    @property
    def rolls(self):
        return [self.roll_1, self.roll_2, self.roll_3, self.roll_4, self.roll_5, self.roll_6]

    @property
    def arc_order(self):
        return ['FL', 'BE', 'FR', 'LF', 'RF', 'LA', 'RA', 'AL', 'AR'].index(self.arc)
