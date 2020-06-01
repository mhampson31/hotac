from django.shortcuts import render
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView


from django.forms import modelformset_factory, inlineformset_factory

from crispy_forms.layout import Submit
from django_tables2 import RequestConfig

from .models import Session, Achievement, Pilot, Event, Campaign, Game, AI, EnemyPilot
from .tables import AchievementTable
from .forms import EnemyPilotForm, SessionForm, make_achievement_form, AchHelper


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
    s = Session.objects.prefetch_related('pilots', 'enemies').get(id=session_id)

    AchForm = make_achievement_form(s)
    AchFormSet = inlineformset_factory(Session, Achievement, form=AchForm, extra=1)
    helper = AchHelper()
    helper.add_input(Submit("submit", "Save"))

    if request.method == 'POST':
        formset = AchFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for ach in instances:
                ach.session = s
                ach.save()
            #formset.save()
            return HttpResponseRedirect(s.get_absolute_url())
    else:
        formset = AchFormSet(queryset=Achievement.objects.filter(session=s))

    ach = s.achievements.values('pilot__callsign', 'event__short_desc') \
                                    .order_by('pilot__id', 'event__id') \
                                    .annotate(total=Count('id'), xp=Coalesce(Sum('threat'), 0) + Sum('event__xp'))

    pilot_list = []
    for p in s.pilots.values('id', 'callsign'):
        achievements = s.achievements.filter(pilot_id=p['id']).values('pilot__callsign', 'event__short_desc') \
                                            .order_by('pilot__id', 'event__id') \
                                            .annotate(total=Count('id'), xp=Coalesce(Sum('threat'), 0) + Sum('event__xp'))
        t = AchievementTable(achievements)

        RequestConfig(request).configure(t)
        t.callsign = p['callsign']
        pilot_list.append(t)

    context = {'pilots': pilot_list,
               'achievements':ach,
               'session':s,
               'formset':formset,
               'helper':helper}

    return render(request, 'campaign/s2.html', context)


def session_plan(request, session_id):
    s = Session.objects.get(id=session_id)
    enemies = s.generate_enemies()

    return render(request, 'campaign/session_plan.html', {'session':s, 'enemies':enemies})


def pilot_sheet(request, pilot_id):
    pilot = Pilot.objects.get(id=pilot_id)

    xp_spent = (pilot.upgrades.aggregate(total=Sum('cost'))['total'] or 0)

    context = {'pilot':pilot,
               'remaining':pilot.total_xp - xp_spent,
               'achievements':pilot.achievement_set.values('event__long_desc', 'target__enemy__chassis__name').annotate(count=Count('event')),
               'missions':pilot.session_set.count()}
    return render(request, 'campaign/pilot.html', context)


class CampaignView(DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaign/campaign.html'


class GameView(DetailView):
    model = Game
    context_object_name = 'game'
    template_name = 'campaign/game.html'


class CampaignUpdate(UpdateView):
    model = Campaign
    fields = ['description', 'victory']


class EnemyView(DetailView):
    model = EnemyPilot
    context_object_name = 'enemy'
    template_name = 'campaign/enemy_pilot.html'


def enemy_list(request):
    enemy_list = EnemyPilot.objects.all()
    context = {'enemy_list':enemy_list}

    return render(request, 'campaign/enemy_list.html', context)


def random_enemy_form(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = EnemyPilotForm.Form(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = EnemyPilotForm()

    return render(request, 'random_enemy_form.html', {'form': form})
