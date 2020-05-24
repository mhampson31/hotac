from django.shortcuts import render
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django_tables2 import RequestConfig

from .models import Session, Pilot, Event, Campaign, AI, EnemyPilot
from .tables import AchievementTable


def index(request):
    current_user = request.user
    context = {'pilots':Pilot.objects.filter(user=current_user.id)}
    return render(request, 'campaign/index.html', context)


def ai_select(request, chassis_slug):
    ai = AI.objects.get(dial__chassis__slug=chassis_slug)
    mvs = ai.aimaneuver_set.filter(range__lte='4')
    fleeing = ai.aimaneuver_set.filter(range='5').first()
    context = {'ai':ai, 'mvs':mvs}
    return render(request, 'campaign/ai.html', context)


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



def pilot_sheet(request, pilot_id):
    pilot = Pilot.objects.get(id=pilot_id)

    xp_spent = (pilot.upgrades.aggregate(total=Sum('cost'))['total'] or 0)

    context = {'pilot':pilot,
               'remaining':pilot.total_xp - xp_spent,
               'achievements':pilot.achievement_set\
                                   .values('event__long_desc')\
                                   .order_by('event__short_desc')\
                                   .annotate(count=Count('event')),
               'missions':pilot.session_set.count()}
    return render(request, 'campaign/pilot.html', context)


class CampaignView(DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaign/campaign.html'


class CampaignUpdate(UpdateView):
    model = Campaign
    fields = ['description', 'victory']


class EnemyView(DetailView):
    model = EnemyPilot
    context_object_name = 'enemy'
    template_name = 'campaign/enemy.html'
