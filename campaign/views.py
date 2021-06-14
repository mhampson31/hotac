from django.shortcuts import render
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.views.generic import DetailView

from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms import modelformset_factory, inlineformset_factory, CheckboxSelectMultiple

from crispy_forms.layout import Submit

from .models import Session, Pilot, PilotUpgrade, Rulebook, Campaign, AI, EnemyPilot
from .forms import EnemyPilotForm, SessionForm, SessionPilotFormset, SessionEnemyFormset, \
                   SPFormsetHelper, PilotUpgradeForm, PUHelper


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


class SessionDebrief(UpdateView):
    model = Session
    form_class = SessionForm
    template_name_suffix = '_debrief'

    def get_success_url(self):
        return reverse_lazy('game:session-debrief', args=(self.object.pk,))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["pilots"] = SessionPilotFormset(self.request.POST, instance=self.object, prefix='pilot')
            enemies = SessionEnemyFormset(self.request.POST, instance=self.object, prefix='enemy')
            for e in enemies:
                e.fields['killed_by'].queryset = self.object.sessionpilot_set.all()
            data["enemies"] = enemies
        else:
            data["pilots"] = SessionPilotFormset(instance=self.object, prefix='pilot')
            enemies = SessionEnemyFormset(instance=self.object, prefix='enemy')
            for e in enemies:
                e.fields['killed_by'].queryset = self.object.sessionpilot_set.all()
            data["enemies"] = enemies
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
        return super().form_valid(form)

    """s = Session.objects.get(id=session_id)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SessionPilotFormset(request.POST, instance=s)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            form.save()
            return HttpResponseRedirect(reverse_lazy('game:session', args=(session_id,)))

    # if a GET (or any other method) we'll create a blank form
    else:
        #form = SessionForm(instance=s)
        form = SessionPilotFormset(instance=s)

    return render(request, 'campaign/session_debrief.html', {'form': form})"""



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
