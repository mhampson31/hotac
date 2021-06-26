from django.contrib import admin

import nested_admin

from .models import Chassis, Slot, Upgrade, Dial, DialManeuver, Faction, Pilot


class DialManeuverInline(nested_admin.NestedTabularInline):
    model = DialManeuver
    extra = 0


class DialInline(nested_admin.NestedTabularInline):
    model = Dial
    inlines = (DialManeuverInline,)


class SlotInline(nested_admin.NestedTabularInline):
    model = Slot
    extra = 1


class ChassisAdmin(nested_admin.NestedModelAdmin):
    verbose_name = 'Chassis'
    list_display = ('name', 'slug', 'dial', 'size')
    inlines = (SlotInline, DialInline)
    fieldsets = (
        (None, {
            'fields': ('name', 'size', 'slug')
        }),
        ('Stats', {
            'fields': (('attack', 'attack_arc'),
                      ('attack2', 'attack2_arc'),
                      ('agility', 'hull', 'shields', 'energy'),
                      ('ability'))
        }),
        ('Miscellaneous', {
            'fields': (('hyperdrive', 'cloaking', 'css'))
        })
    )


class UpgradeAdmin(admin.ModelAdmin):
    model = Upgrade
    list_display = ('name', 'type', 'type2', 'cost', 'charges')
    list_filter = ('type',)


class FactionAdmin(admin.ModelAdmin):
    filter_horizontal = ('ships',)


class PilotCardAdmin(admin.ModelAdmin):
    model = Pilot
    list_display = ('name', 'faction', 'chassis', 'initiative')
    list_filter = ('faction', 'chassis', 'initiative')
    exclude = ('type', 'type2')


admin.site.register(Pilot, PilotCardAdmin)
admin.site.register(Upgrade, UpgradeAdmin)
admin.site.register(Chassis, ChassisAdmin)
admin.site.register(Faction, FactionAdmin)
