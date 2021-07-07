from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

import nested_admin

from .models import User, Rulebook, PlayableShip, Pilot, Mission, \
    Campaign, Session, SessionEnemy, SessionPilot, PilotShip, PilotUpgrade, FGSetup, FlightGroup, \
    AI, AIManeuver, AIPriority, EnemyPilot, EnemyAbility, Ally
from xwtools.models import Card

#from xwtools.models import Slot


class PilotInline(admin.StackedInline):
    model = Pilot
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (PilotInline, )


class FGSetupInline(nested_admin.NestedTabularInline):
    model = FGSetup
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'object_id' in request.resolver_match.kwargs:
            if db_field.name == 'chassis':
                kwargs['queryset'] = Mission.objects.get(pk=request.resolver_match.kwargs['object_id']).enemy_faction.ships.all()
                kwargs['initial'] = Mission.objects.get(pk=request.resolver_match.kwargs['object_id']).enemy_faction.default_ship
            elif db_field.name == 'flight_group':
                kwargs['queryset'] = FlightGroup.objects.filter(mission_id=request.resolver_match.kwargs['object_id'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



class FlightGroupInline(nested_admin.NestedTabularInline):
    model = FlightGroup
    inlines = (FGSetupInline,)
    extra = 0


class AllyInline(nested_admin.NestedTabularInline):
    model = Ally
    extra = 0
    fields = ('callsign', 'chassis', 'initiative', 'abilities')
    filter_horizontal = ('abilities',)


class MissionAdmin(nested_admin.NestedModelAdmin):
    model = Mission
    inlines = (AllyInline, FlightGroupInline)
    list_display = ['rulebook', 'name', 'story', 'sequence']


class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    list_display = ['description', 'rulebook', 'gm']
    filter_horizontal = ['deck', 'exclude_random']


class SessionEnemyInline(admin.TabularInline):
    model = SessionEnemy
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'object_id' in request.resolver_match.kwargs:
            if db_field.name == 'flight_group':
                kwargs['queryset'] = Session.objects.get(pk=request.resolver_match.kwargs['object_id']).mission.flight_groups.all()
            elif db_field.name == 'killed_by':
                kwargs['queryset'] = SessionPilot.objects.filter(session__pk=request.resolver_match.kwargs['object_id'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SessionPilotInline(admin.TabularInline):
    model = SessionPilot
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'object_id' in request.resolver_match.kwargs:
            if db_field.name == 'pilot':
                kwargs['queryset'] = Session.objects.get(pk=request.resolver_match.kwargs['object_id']).campaign.pilots.all()
            elif db_field.name == 'ship':
                c = Session.objects.get(pk=request.resolver_match.kwargs['object_id']).campaign
                kwargs['queryset'] = PilotShip.objects.filter(pilot__campaign=c)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SessionAdmin(admin.ModelAdmin):
    inlines = (SessionEnemyInline, SessionPilotInline)
    list_display = ['mission', 'campaign', 'date', 'outcome']


class PlayableShipInline(admin.TabularInline):
    model = PlayableShip
    extra = 1


class RulebookAdmin(admin.ModelAdmin):
    model = Rulebook
    inlines = (PlayableShipInline,)


class PilotShipInline(admin.TabularInline):
    model = PilotShip
    extra = 0


class PilotUpgradeInline(admin.TabularInline):
    model = PilotUpgrade
    extra = 0

class PilotAdmin(admin.ModelAdmin):
    model = Pilot
    list_display = ('callsign', 'campaign', 'user')
    list_filter = ('campaign', 'user')
    inlines = (PilotShipInline, PilotUpgradeInline)


class PilotShipAdmin(admin.ModelAdmin):
    model = PilotShip
    list_display = ('pilot', 'chassis')


class AIManeuverInline(admin.TabularInline):
    model = AIManeuver
    extra = 0

    fieldsets = (
        (None, {'fields': ('arc', 'range')}),
        ('Rolls', {'fields': ('roll_1', 'roll_2', 'roll_3', 'roll_4', 'roll_5', 'roll_6')})
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'object_id' in request.resolver_match.kwargs:
            if db_field.name in ('roll_1', 'roll_2', 'roll_3', 'roll_4', 'roll_5', 'roll_6'):
                kwargs['queryset'] = AI.objects.get(pk=request.resolver_match.kwargs['object_id']).dial.maneuvers.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AIPriorityInline(admin.TabularInline):
    model = AIPriority
    extra = 0


class AIAdmin(admin.ModelAdmin):
    inlines = (AIPriorityInline, AIManeuverInline)


class EnemyAbilityInline(admin.TabularInline):
    model = EnemyAbility
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'card':
            kwargs['queryset'] = Card.objects.filter(ai_use=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class EnemyPilotAdmin(admin.ModelAdmin):
    inlines = (EnemyAbilityInline,)
    list_display = ('chassis', 'faction', 'basic', 'elite', 'in3', 'in4', 'in5')



#admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Pilot, PilotAdmin)
admin.site.register(Rulebook, RulebookAdmin)
admin.site.register(Mission, MissionAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(AI, AIAdmin)
admin.site.register(EnemyPilot, EnemyPilotAdmin)
