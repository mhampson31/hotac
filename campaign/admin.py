from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


from .models import User, Campaign, Pilot, Event, Mission, Session, Achievement, Ship, Slot, PilotShip


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


class ShipAdmin(admin.ModelAdmin):
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

    def get_form(self, request, obj=None, **kwargs):
            form = super(CompanyAdmin, self).get_form(request, obj, **kwargs)
            form.fields['theme'].queryset = Theme.objects.filter(name__iexact='company')
            return form


#admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Pilot)
admin.site.register(Campaign)
admin.site.register(Mission)
admin.site.register(Event)
admin.site.register(Ship, ShipAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(PilotShip)
