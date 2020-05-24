from django.contrib import admin

from .models import Chassis, Slot, Upgrade, Dial, DialManeuver, Faction


class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1


class ChassisAdmin(admin.ModelAdmin):
    list_display = ['name', 'faction']
    list_filter = ['faction',]
    verbose_name = 'Chassis'
    inlines = (SlotInline, )


class UpgradeAdmin(admin.ModelAdmin):
    model = Upgrade
    list_display = ('name', 'type', 'type2', 'cost', 'charges')


class DialManeuverInline(admin.TabularInline):
    model = DialManeuver
    extra = 0


class DialAdmin(admin.ModelAdmin):
    inlines = (DialManeuverInline,)


admin.site.register(Upgrade, UpgradeAdmin)
admin.site.register(Dial, DialAdmin)
admin.site.register(Chassis, ChassisAdmin)
admin.site.register(Faction)
