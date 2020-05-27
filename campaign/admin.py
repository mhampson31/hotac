from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Campaign, Squadron, Pilot, Event, Mission, \
    Session, Achievement, PilotShip, SquadMember, FlightGroup, \
    AI, AIManeuver, \
    EnemyPilot, EnemyAbility, EnemyUpgrade

#from xwtools.models import Slot


class PilotInline(admin.StackedInline):
    model = Pilot

class UserAdmin(BaseUserAdmin):
    inlines = (PilotInline, )


class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 1


class SquadMemberInline(admin.TabularInline):
    model = SquadMember
    extra = 0

class FlightGroupInline(admin.TabularInline):
    model = FlightGroup
    extra = 0


class MissionAdmin(admin.ModelAdmin):
    model = Mission
    inlines = (FlightGroupInline, SquadMemberInline)


class SessionAdmin(admin.ModelAdmin):
    inlines = (AchievementInline,)


class SquadronInline(admin.TabularInline):
    model = Squadron
    extra = 1


class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    inlines = (SquadronInline,)


class PilotAdmin(admin.ModelAdmin):
    model = Pilot
    list_display = ('callsign', 'campaign', 'user', 'total_xp')
    filter_horizontal = ('upgrades',)


class PilotShipInline(admin.StackedInline):
    model = PilotShip
    extra = 0


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


class AIAdmin(admin.ModelAdmin):
    inlines = (AIManeuverInline,)


class EnemyAbilityInline(admin.TabularInline):
    model = EnemyAbility
    extra = 0


class EnemyPilotAdmin(admin.ModelAdmin):
    inlines = (EnemyAbilityInline,)
    list_display = ('chassis', 'faction', 'basic', 'elite', 'in3', 'in4', 'in5')



#admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Pilot, PilotAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Mission, MissionAdmin)
admin.site.register(Event)
admin.site.register(Session, SessionAdmin)
admin.site.register(PilotShip, PilotShipAdmin)
admin.site.register(AI, AIAdmin)
admin.site.register(EnemyUpgrade)
admin.site.register(EnemyPilot, EnemyPilotAdmin)
