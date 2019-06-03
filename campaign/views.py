from django.shortcuts import render
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce

from django_tables2 import RequestConfig

from .models import Session, Pilot, Event, Campaign
from .tables import AchievementTable


def index(request):
    current_user = request.user
    context = {'pilots':Pilot.objects.filter(user=current_user.id)}
    return render(request, 'campaign/index.html', context)


def session_summary(request, session_id):
    s = Session.objects.get(id=session_id)

    pilot_list = []
    for p in s.pilots.values('id', 'callsign'):
        t = AchievementTable(s.achievement_set.filter(pilot_id=p['id']).values('pilot__callsign', 'event__short_desc')
                                            .order_by('pilot__id', 'event__id')
                                            .annotate(total=Count('id'), xp=Coalesce(Sum('threat'), 0) + Sum('event__xp')))

        RequestConfig(request).configure(t)
        t.callsign = p['callsign']
        pilot_list.append(t)
    return render(request, 'campaign/s2.html', {'pilots': pilot_list, 'session':s})


def old_session_summary(request, session_id):
    context = {'session_summary':Session.objects.get(id=session_id)
                                        .achievement_set
                                        .values('pilot__callsign', 'event__short_desc')
                                        .order_by('pilot__id', 'event__id')
                                        .annotate(total=Count('id'), xp=Coalesce(Sum('threat'), 0) + Sum('event__xp'))
    }
    return render(request, 'campaign/session.html', context)


def pilot_sheet(request, pilot_id):
    pilot = Pilot.objects.get(id=pilot_id)
    ach = []
    for ev in Event.objects.all():
        a = pilot.achievement_set.filter(event=ev.id)
        if a:
            ach.append({'event':ev.long_desc, 'count':len(a)})
    context = {'pilot':pilot,
               'spent':(pilot.upgrades.aggregate(total=Sum('cost'))['total'] or 0) +
                       pilot.pilotship_set.aggregate(total=Sum('unlocked__cost'))['total'],
               'achievements':ach,
               'missions':len(pilot.session_set.all())}
    return render(request, 'campaign/pilot.html', context)


def campaign(request, campaign_id):
    return
