from django.contrib import admin

import nested_admin

from .models import Chassis, Slot, Dial, DialManeuver, Faction, Card, UpgradeCard, PilotCard, ShipAbility
from .models import SlotChoice, Attack, Action


class DialManeuverInline(nested_admin.NestedTabularInline):
    model = DialManeuver
    extra = 0


class DialInline(nested_admin.NestedTabularInline):
    model = Dial
    inlines = (DialManeuverInline,)


class SlotInline(nested_admin.NestedTabularInline):
    model = Slot
    extra = 1


class ActionInline(nested_admin.NestedTabularInline):
    model = Action
    extra = 0


class ChassisAdmin(nested_admin.NestedModelAdmin):
    verbose_name = 'Chassis'
    list_display = ('name', 'slug', 'dial', 'size')
    list_select_related = ('dial',)
    inlines = (ActionInline, SlotInline, DialInline)
    fieldsets = (
        (None, {
            'fields': ('name', 'size', 'slug')
        }),
        ('Stats', {
            'fields': (('attack', 'attack_arc'),
                      ('attack2', 'attack2_arc'),
                      ('agility', 'hull', 'shields'),
                      ('energy', ),
                      ('walker', 'armor'),
                      ('ability'))
        }),
        ('Miscellaneous', {
            'fields': (('hyperdrive', 'css'))
        })
    )


class FactionAdmin(admin.ModelAdmin):
    filter_horizontal = ('ships',)


class PilotCardAdmin(admin.ModelAdmin):
    model = PilotCard
    list_display = ('name', 'faction', 'chassis', 'initiative', 'player_use', 'ai_use', 'limited')
    list_filter = ('faction', 'chassis', 'initiative', 'player_use', 'ai_use')
    list_editable = ('chassis', 'initiative', 'player_use', 'ai_use', 'limited')

    fields = ('name', 'limited', 'description', 'ai_description', 'type', 'faction', 'chassis', 'initiative', 'charges', 'recurring', 'force', 'ai_use')

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "type":
            kwargs['choices'] = ( (SlotChoice.PILOT.value, SlotChoice.PILOT.label), )
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class ShipAbilityAdmin(admin.ModelAdmin):
    model = ShipAbility
    fields = ('name', 'description', 'ai_description', 'type', 'player_use', 'ai_use')

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "type":
            kwargs['choices'] = ( (SlotChoice.SHIP.value, SlotChoice.SHIP.label), )
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class AttackInline(admin.TabularInline):
    model = Attack
    extra = 0


class UpgradeCardAdmin(admin.ModelAdmin):
    model = UpgradeCard
    list_display = ('name', 'type', 'cost', 'charges', 'recurring', 'repeat', 'player_use', 'ai_use', 'limited')
    list_filter = ('type', 'player_use', 'ai_use')
    list_editable = ('cost', 'repeat', 'recurring', 'player_use', 'ai_use', 'limited')
    inlines = (AttackInline,)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'ai_description',
                       ('limited', 'type', 'type2', 'cost', 'repeat'),
                       ('charges', 'recurring', 'force'),
                       ('requires', 'adds',),
                       ('player_use', 'ai_use')
                      )
        }),
    )

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "type":
            slots = SlotChoice.choices
            slots.remove((SlotChoice.PILOT.value, SlotChoice.PILOT.label))
            slots.remove((SlotChoice.SHIP.value, SlotChoice.SHIP.label))
            kwargs['choices'] = (slots)
        return super().formfield_for_choice_field(db_field, request, **kwargs)


admin.site.register(ShipAbility, ShipAbilityAdmin)
admin.site.register(UpgradeCard, UpgradeCardAdmin)
admin.site.register(PilotCard, PilotCardAdmin)

admin.site.register(Chassis, ChassisAdmin)
admin.site.register(Faction, FactionAdmin)
