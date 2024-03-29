from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.views.generic import DetailView

from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms import modelformset_factory, inlineformset_factory, CheckboxSelectMultiple
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from crispy_forms.layout import Submit

from rest_framework import viewsets
from rest_framework import permissions
from .serializers import PilotSerializer, UserSerializer


from .models import Session, Pilot, PilotShip, PilotUpgrade, Rulebook, Campaign, AI, EnemyPilot, User
from .forms import EnemyPilotForm, SessionForm, SessionPilotFormset, SessionEnemyFormset, \
                   SPFormsetHelper, SEFormsetHelper, PUHelper, AddUpgrade, \
                   CampaignForm, SessionPlanForm, AddSessionPilotFormset, SessionPilotHelper, PilotUpdateForm

from xwtools.models import SlotChoice, Card
import datetime

# ### API views ### #

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class PilotViewSet(viewsets.ModelViewSet):
    queryset = Pilot.objects.all()
    serializer_class = PilotSerializer

# ### Frontend views ### #

@login_required
def player_page(request, player_id=None):
    if player_id:
        player = get_object_or_404(User, pk=player_id)
    else:
        player = request.user

    context = {'player':player}
    return render(request, 'campaign/player.html', context)


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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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
    initial = {'date':datetime.date.today}

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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
        if pilots.is_valid() and enemies.is_valid():
            self.object = form.save(commit=False)
            pilots.instance = self.object
            pilots.save()
            enemies.instance = self.object
            enemies.save()
            self.object.debrief()
            self.object.save()

        else:
            return self.form_invalid(form)
        return super().form_valid(form)


def session_plan(request, session_id):
    s = Session.objects.get(id=session_id)
    enemies = s.generate_enemies()

    return render(request, 'campaign/session_plan.html', {'session':s, 'enemies':enemies})


class PilotUpdate(UpdateView):
    model = Pilot
    context_object_name = 'pilot'
    template_name = 'campaign/pilot.html'
    form_class = PilotUpdateForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self, **kwargs):
        return Pilot.objects.select_related('campaign',)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        pilot = self.object
        if self.request.method == 'POST':
            update_form = AddUpgrade(self.request.POST, initial={'pilot':pilot, 'status':'E', 'cost':0})
        else:
            update_form = AddUpgrade(initial={'pilot':pilot, 'status':'E', 'cost':0})
        update_form.fields['card'].queryset = pilot.available_upgrades
        data['update'] = update_form
        data['remaining'] = pilot.total_xp - pilot.spent_xp
        if pilot.initiative < 6:
            data['init_upgrade_cost'] = pilot.campaign.rulebook.get_initiative_cost(pilot.initiative+1)
        return data

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        upgrade_form = context['update']
        if upgrade_form.is_valid() and upgrade_form.cleaned_data['card']:
            new_upgrade = upgrade_form.save(commit=False)
            new_upgrade.pilot = self.object
            new_upgrade.cost = new_upgrade.card.campaign_cost(self.object.campaign.rulebook.upgrade_logic)
            new_upgrade.status = 'E'
            new_upgrade.save()
        else:
            print(upgrade_form.errors)
        return super().form_valid(form)


class RulebookView(DetailView):
    model = Rulebook
    context_object_name = 'Rulebook'
    template_name = 'campaign/rulebook.html'


class CampaignView(DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaign/campaign.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CampaignUpdate(UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name_suffix = '_plan'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class RulebookUpdate(UpdateView):
    model = Rulebook
    fields = ['description', 'victory']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


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
