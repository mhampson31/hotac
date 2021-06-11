from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Rulebook, PlayableShip, Pilot, Event, Mission, \
    Campaign, Session, SessionEnemy, SessionPilot, PilotShip, PilotUpgrade, FGSetup, FlightGroup, \
    AI, AIManeuver, AIPriority, \
    EnemyPilot, EnemyAbility

#from xwtools.models import Slot


class PilotInline(admin.StackedInline):
    model = Pilot


class UserAdmin(BaseUserAdmin):
    inlines = (PilotInline, )


class FGSetupInline(admin.TabularInline):
    model = FGSetup
    extra = 0


class FlightGroupInline(admin.TabularInline):
    model = FlightGroup
    extra = 0


class MissionAdmin(admin.ModelAdmin):
    model = Mission
    inlines = (FlightGroupInline, FGSetupInline)


class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    list_display = ['description', 'rulebook', 'gm']


class SessionEnemyInline(admin.TabularInline):
    model = SessionEnemy
    extra = 0

class SessionPilotInline(admin.TabularInline):
    model = SessionPilot
    extra = 0

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

class AIPriorityInline(admin.TabularInline):
    model = AIPriority
    extra = 0

class AIAdmin(admin.ModelAdmin):
    inlines = (AIPriorityInline, AIManeuverInline)


class EnemyAbilityInline(admin.TabularInline):
    model = EnemyAbility
    extra = 0


class EnemyPilotAdmin(admin.ModelAdmin):
    inlines = (EnemyAbilityInline,)
    list_display = ('chassis', 'faction', 'basic', 'elite', 'in3', 'in4', 'in5')



#admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Pilot, PilotAdmin)
admin.site.register(Rulebook, RulebookAdmin)
admin.site.register(Mission, MissionAdmin)
admin.site.register(Event)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(AI, AIAdmin)
admin.site.register(EnemyPilot, EnemyPilotAdmin)
