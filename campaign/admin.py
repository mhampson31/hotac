from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Campaign, CampaignShip, Pilot, Event, Mission, \
    Session, Achievement, PilotShip, AI, AIManeuver

from xwtools.models import Slot


class PilotInline(admin.StackedInline):
    model = Pilot

class UserAdmin(BaseUserAdmin):
    inlines = (PilotInline, )


class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 1


class SessionAdmin(admin.ModelAdmin):
    inlines = (AchievementInline, )


class CampaignShipInline(admin.TabularInline):
    model = CampaignShip
    extra = 1


class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    inlines = (CampaignShipInline,)


class PilotAdmin(admin.ModelAdmin):
    model = Pilot
    list_display = ('callsign', 'campaign', 'user', 'total_xp')
    filter_horizontal = ('upgrades',)


class PilotShipInline(admin.StackedInline):
    model = PilotShip
    extra = 0


class UnlockedInline(admin.TabularInline):
    model = Slot
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(author=request.user)


class PilotShipAdmin(admin.ModelAdmin):
    model = PilotShip
    list_display = ('pilot', 'ship')


class AIManeuverInline(admin.TabularInline):
    model = AIManeuver
    extra = 0

    fieldsets = (
        (None, {'fields': ('arc', 'range')}),
        ('Rolls', {'fields': ('roll_1', 'roll_2', 'roll_3', 'roll_4', 'roll_5', 'roll_6')})
    )


class AIAdmin(admin.ModelAdmin):
    inlines = (AIManeuverInline,)


#admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Pilot, PilotAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Mission)
admin.site.register(Event)
admin.site.register(Session, SessionAdmin)
admin.site.register(PilotShip, PilotShipAdmin)
admin.site.register(AI, AIAdmin)
