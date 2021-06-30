from django.contrib import admin

import nested_admin

from .models import Chassis, Slot, Upgrade, Dial, DialManeuver, Faction, Card, UpgradeCard, PilotCard2
from .models import SlotChoice

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
    model = PilotCard2
    list_display = ('name', 'faction', 'chassis', 'initiative')
    list_editable = ('chassis', 'initiative')

    fields = ('name', 'description', 'ai_description', 'type', 'faction', 'initiative', 'chassis', 'charges', 'force')


    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "type":
            kwargs['choices'] = ( (SlotChoice.PILOT.value, SlotChoice.PILOT.label), )
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class UpgradeCardAdmin(admin.ModelAdmin):
    model = UpgradeCard
    list_display = ('name', 'type', 'cost', 'charges', 'repeat')
    list_filter = ('type',)
    list_editable = ('cost', 'repeat')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'ai_description',
                       ('type', 'type2', 'repeat'),
                       ('charges', 'force')
                      )
        }),
    )
    #fields = ('name', 'description', 'ai_description', 'type', 'faction', 'initiative', 'chassis', 'charges', 'force')

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "type":
            slots = SlotChoice.choices
            slots.remove((SlotChoice.PILOT.value, SlotChoice.PILOT.label))
            slots.remove((SlotChoice.SHIP.value, SlotChoice.SHIP.label))
            kwargs['choices'] = (slots)
        return super().formfield_for_choice_field(db_field, request, **kwargs)


admin.site.register(UpgradeCard, UpgradeCardAdmin)
admin.site.register(PilotCard2, PilotCardAdmin)

admin.site.register(Chassis, ChassisAdmin)
admin.site.register(Faction, FactionAdmin)
