from django.shortcuts import render
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms import modelformset_factory, inlineformset_factory, CheckboxSelectMultiple

from crispy_forms.layout import Submit

from .models import Session, Pilot, PilotUpgrade, Event, Rulebook, Campaign, AI, EnemyPilot
from .forms import EnemyPilotForm, SessionForm, PilotUpgradeForm, PUHelper


def index(request):
    current_user = request.user
    context = {'campaigns':Campaign.objects.filter(pilot__user=current_user.id).distinct(),
               'ais':AI.objects.all()}
    #context = {'pilots':Pilot.objects.filter(user=current_user.id)}
    return render(request, 'campaign/index.html', context)


def ai_select(request, chassis_slug):
    ai = AI.objects.get(dial__chassis__slug=chassis_slug)
    mvs = ai.aimaneuver_set.all().select_related('roll_1', 'roll_2', 'roll_3', 'roll_4', 'roll_5', 'roll_6')
    targets = ai.priorities.filter(type='T')
    actions = ai.priorities.filter(type='A')
    context = {'ai':ai, 'mvs':mvs, 'targets':targets, 'actions':actions}
    return render(request, 'campaign/ai.html', context)


def session_summary(request, session_id):
    s = Session.objects.get(id=session_id)
    init_list = [e for e in s.sessionenemy_set.all()] + \
                [p for p in s.sessionpilot_set.all()]
    init_list.sort(key=lambda init: init.initiative)
    enemy_count = s.enemies.values('chassis__name').annotate(ship_count=Count('id'))

    context = {'session':s, 'init_list':init_list, 'enemy_count':enemy_count}
    return render(request, 'campaign/session.html', context)

def session_plan(request, session_id):
    s = Session.objects.get(id=session_id)
    enemies = s.generate_enemies()

    return render(request, 'campaign/session_plan.html', {'session':s, 'enemies':enemies})

def pilot_sheet(request, pk):
    pilot = Pilot.objects.get(id=pk)

    UpgradeFormSet = inlineformset_factory(Pilot, PilotUpgrade,
                                           form=PilotUpgradeForm,
                                           exclude=('lost',),
                                           extra=1)
    helper = PUHelper()
    helper.add_input(Submit("submit", "Save"))

    if request.method == 'POST':
        update_form = UpgradeFormSet(request.POST, instance=pilot)

        if update_form.is_valid():
            update_form.save()
            return HttpResponseRedirect(pilot.get_absolute_url())
    else:
        update_form = UpgradeFormSet(instance=pilot)

    context = {'pilot':pilot,
               'remaining':pilot.total_xp - pilot.spent_xp,
               'update': update_form,
               'helper': helper}
    return render(request, 'campaign/pilot.html', context)


class RulebookView(DetailView):
    model = Rulebook
    context_object_name = 'Rulebook'
    template_name = 'campaign/rulebook.html'


class CampaignView(DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaign/campaign.html'


class RulebookUpdate(UpdateView):
    model = Rulebook
    fields = ['description', 'victory']


class EnemyView(DetailView):
    model = EnemyPilot
    context_object_name = 'enemy'
    template_name = 'campaign/enemy_pilot.html'


class PilotUpdate(DetailView):
    model = Pilot
    context_object_name = 'pilot'
    template_name = 'campaign/pilot_update.html'
    fields = ('callsign', 'upgrades')


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
