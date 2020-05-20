from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter

from .models import User, Campaign, Pilot, Event, Mission, \
    Session, Achievement, Ship, Slot, PilotShip, \
    Upgrade, TreeSlot, Dial, DialManeuver, AI, AIManeuver


class PilotInline(admin.StackedInline):
    model = Pilot

class UserAdmin(BaseUserAdmin):
    inlines = (PilotInline, )


class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 1

class SessionAdmin(admin.ModelAdmin):
    inlines = (AchievementInline, )


class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1


class PilotAdmin(admin.ModelAdmin):
    model = Pilot
    list_display = ('callsign', 'campaign', 'user', 'total_xp')
    filter_horizontal = ('upgrades',)

class ShipAdmin(admin.ModelAdmin):
    list_display = ['name', 'faction', 'playable']
    list_filter = ['faction', 'playable']
    inlines = (SlotInline, )


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
    filter_horizontal = ('unlocked',)


class UpgradeAdmin(admin.ModelAdmin):
    model = Upgrade
    list_display = ('name', 'type', 'type2', 'cost', 'charges')


class TreeSlotAdmin(DraggableMPTTAdmin):
    model = TreeSlot
    list_display = ('tree_actions', 'indented_title', 'ship', 'threat', 'cost', 'type')
    list_filter = (
        ('treeslot', TreeRelatedFieldListFilter),
    )


class DialManeuverInline(admin.TabularInline):
    model = DialManeuver
    extra = 0

class DialAdmin(admin.ModelAdmin):
    inlines = (DialManeuverInline,)


class AIManeuverInline(admin.TabularInline):
    model = AIManeuver
    extra = 0

    fieldsets = (
        (None, {'fields': ('arc', 'range')}),
        ('Rolls', {'fields': ('roll_1', 'roll_2', 'roll_3', 'roll_4', 'roll_5', 'roll_6')})
    )

#    def get_form(self, request, obj=None, **kwargs):
 #       form = super(AIManeuverInline, self).get_form(request, obj, **kwargs)

  #      form.base_fields['roll_1'].queryset = DialManeuver.objects.filter(dial_id=obj.ai.dial.id)

   #     return form


class AIAdmin(admin.ModelAdmin):
    inlines = (AIManeuverInline,)


#admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Pilot, PilotAdmin)
#admin.site.register(Upgrade, UpgradeAdmin)
#admin.site.register(Dial, DialAdmin)
admin.site.register(Campaign)
admin.site.register(Mission)
admin.site.register(Event)
#admin.site.register(Ship, ShipAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(PilotShip, PilotShipAdmin)
#admin.site.register(TreeSlot, TreeSlotAdmin)
admin.site.register(AI, AIAdmin)
