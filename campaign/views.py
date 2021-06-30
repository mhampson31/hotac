from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.views.generic import DetailView

from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms import modelformset_factory, inlineformset_factory, CheckboxSelectMultiple

from crispy_forms.layout import Submit

from .models import Session, Pilot, PilotShip, PilotUpgrade, Rulebook, Campaign, AI, EnemyPilot, CampaignUpgrade
from .forms import EnemyPilotForm, SessionForm, SessionPilotFormset, SessionEnemyFormset, \
                   SPFormsetHelper, SEFormsetHelper, PUHelper, AddUpgrade, \
                   CampaignForm, SessionPlanForm, AddSessionPilotFormset, SessionPilotHelper

from xwtools.models import SlotChoice, OldPilotCard, Card


def index(request):
    current_user = request.user
    context = {'campaigns':Campaign.objects.filter(pilots__user=current_user.id).distinct(),
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
    init_list = list(s.sessionenemy_set.all()) + list(s.sessionpilot_set.all()) + list(s.mission.allies.all())
    init_list.sort(key=lambda init: init.initiative)
    enemy_count = s.enemies.values('chassis__name').annotate(ship_count=Count('id'))

    context = {'session':s, 'init_list':init_list, 'enemy_count':enemy_count}
    return render(request, 'campaign/session.html', context)


class SessionPlan(CreateView):
    model = Session
    form_class = SessionPlanForm
    template_name_suffix = '_plan'

    def get_initial(self):
        initial = super().get_initial()
        initial['campaign'] = get_object_or_404(Campaign, id=self.kwargs.get("pk"))
        pilots = initial['campaign'].pilots.all()
        return initial

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['pilots'] = AddSessionPilotFormset(self.request.POST, instance=self.object, prefix='pilot')
        else:
            data['pilots'] = AddSessionPilotFormset(instance=self.object, prefix='pilot')
        #for p in data['pilots']:
        #    p.fields['ship'].queryset = PilotShip.objects.filter(pilot_id=p.fields['id'])
        data['pilot-helper'] = SessionPilotHelper
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        self.object = form.save()
        for p in self.object.campaign.pilots.all():
            self.object.sessionpilot_set.create(session=self.object, pilot=p,
                                                ship=p.active_ship,
                                                initiative=p.initiative)
        self.object.generate_enemies()
        return super().form_valid(form)


class SessionDebrief(UpdateView):
    model = Session
    form_class = SessionForm
    template_name_suffix = '_debrief'

    def get_success_url(self):
        return reverse_lazy('game:campaign', args=(self.object.campaign.pk,))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["pilots"] = SessionPilotFormset(self.request.POST, instance=self.object, prefix='pilot')
            data['enemies'] = SessionEnemyFormset(self.request.POST, instance=self.object, prefix='enemy')
            for e in data['enemies']:
                e.fields['killed_by'].queryset = self.object.sessionpilot_set.all()
        else:
            data["pilots"] = SessionPilotFormset(instance=self.object, prefix='pilot')
            data['enemies'] = SessionEnemyFormset(instance=self.object, prefix='enemy')
            for e in data['enemies']:
                e.fields['killed_by'].queryset = self.object.sessionpilot_set.all()
        data["pilot-helper"] = SPFormsetHelper
        data["enemy-helper"] = SEFormsetHelper
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        pilots = context["pilots"]
        enemies = context["enemies"]
        self.object = form.save()
        if pilots.is_valid():
            pilots.instance = self.object
            pilots.save()
        if enemies.is_valid():
            enemies.instance = self.object
            enemies.save()
        self.object.debrief()
        return super().form_valid(form)


def session_plan(request, session_id):
    s = Session.objects.get(id=session_id)
    enemies = s.generate_enemies()

    return render(request, 'campaign/session_plan.html', {'session':s, 'enemies':enemies})


def pilot_sheet(request, pk):
    pilot = Pilot.objects.select_related('user', 'campaign').get(id=pk)

    if request.method == 'POST':
        update_form = AddUpgrade(request.POST, initial={'pilot':pilot.id, 'status':'E'})

        if update_form.is_valid():
            update_form.save()
            return HttpResponseRedirect(pilot.get_absolute_url())
        else:
            print(update_form.errors)
    else:
        update_form = AddUpgrade(initial={'pilot':pilot, 'status':'E'})

    update_form.fields['card'].queryset = pilot.available_upgrades
    context = {'pilot':pilot,
               'remaining':pilot.total_xp - pilot.spent_xp,
               'update': update_form}
    return render(request, 'campaign/pilot.html', context)


class RulebookView(DetailView):
    model = Rulebook
    context_object_name = 'Rulebook'
    template_name = 'campaign/rulebook.html'


class CampaignView(DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaign/campaign.html'


class CampaignUpdate(UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name_suffix = '_plan'


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
