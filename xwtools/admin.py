from django.contrib import admin

from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter

from .models import Ship, Slot, Upgrade, TreeSlot, Dial, DialManeuver


class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1


class ShipAdmin(admin.ModelAdmin):
    list_display = ['name', 'faction']
    list_filter = ['faction',]
    inlines = (SlotInline, )


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


admin.site.register(Upgrade, UpgradeAdmin)
admin.site.register(Dial, DialAdmin)
admin.site.register(Ship, ShipAdmin)
admin.site.register(TreeSlot, TreeSlotAdmin)
