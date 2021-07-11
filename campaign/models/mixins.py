from django.db import models
from django.utils.functional import cached_property

from xwtools.models import Chassis

class DisplayShipMixin(models.Model):

    class Meta:
        abstract = True

    @cached_property
    def shields(self):
        return self.chassis.shields + \
               self.abilities.filter(card__adds__contains='+[Shield', status='E').count() - \
               self.abilities.filter(card__adds__contains='-[Shield', status='E').count()

    @cached_property
    def hull(self):
        return self.chassis.hull + \
               self.abilities.filter(card__adds__contains='+[Hull', status='E').count() - \
               self.abilities.filter(card__adds__contains='-[Hull', status='E').count()

    @cached_property
    def hull(self):
        return self.chassis.energy + \
               self.abilities.filter(card__adds__contains='+[Energy', status='E').count() - \
               self.abilities.filter(card__adds__contains='-[Energy', status='E').count()
