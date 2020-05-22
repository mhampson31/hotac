from django.contrib import admin

from .models import Chassis, Slot, Upgrade, Dial, DialManeuver


class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1


class ChassisAdmin(admin.ModelAdmin):
    list_display = ['name', 'faction']
    list_filter = ['faction',]
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
