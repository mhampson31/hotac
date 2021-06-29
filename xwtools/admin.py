from django.contrib import admin

import nested_admin

from .models import Chassis, Slot, Upgrade, Dial, DialManeuver, Faction, PilotCard


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
    list_select_related = ('dial',)
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
    list_display = ('name', 'type', 'type2', 'cost', 'charges', 'for_players', 'for_ai')
    list_filter = ('type',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'ai_description',
                       ('type', 'type2', 'repeat'),
                       ('charges', 'force'),
            )
        }),
        ('Adds', {
            'fields': ('attack_requires',
                        ('attack_arc', 'attack_dice'),
                        ('attack_range', 'attack_ordnance'),
                        'adds'
                    )
        })
    )


class FactionAdmin(admin.ModelAdmin):
    filter_horizontal = ('ships',)


class PilotCardAdmin(admin.ModelAdmin):
    model = PilotCard
    list_display = ('name', 'faction', 'chassis', 'initiative')
    list_filter = ('faction', 'chassis', 'initiative')
    exclude = ('type', 'type2')


admin.site.register(PilotCard, PilotCardAdmin)
admin.site.register(Upgrade, UpgradeAdmin)
admin.site.register(Chassis, ChassisAdmin)
admin.site.register(Faction, FactionAdmin)
