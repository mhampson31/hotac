from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field

from .models import EnemyPilot, EnemyAbility, Session, Pilot, PilotUpgrade, Achievement, CampaignUpgrade
from .fields import GroupedModelChoiceField
from xwtools.models import Upgrade, SlotChoice



class EnemyPilotForm(forms.Form):
    pass
#    level = forms.ChoiceField(EnemyAbility.Level.choices)



class AchHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form-inline'
        self.layout = Layout(
            'turn',
            'pilot',
            'event',
            'target'
        )
        self.render_required_fields = True


class PUHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form-horizontal'
        self.form_show_labels = False
        self.layout = Layout(
            Div(
                Field('upgrade', wrapper_class='col-4'),
                Field('copies', wrapper_class='col-1'),
                Field('status', wrapper_class='col-2'),
                css_class='form-group row'
            )
        )
        self.render_required_fields = True


class SessionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        helper.form_class = 'form-inline'
        helper.field_template = 'bootstrap4/layout/inline_field.html'

        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Session
        fields = ['date', 'outcome']


class PilotUpgradeForm(forms.ModelForm):
    from operator import methodcaller

    upgrade = GroupedModelChoiceField(queryset=CampaignUpgrade.objects.all(),
                                      choices_groupby=methodcaller('get_type_display'))
    copies = forms.IntegerField(min_value=1)
    status = forms.ChoiceField(choices=PilotUpgrade.UStatusChoice.choices)

    class Meta:
        model = PilotUpgrade
        fields = ('upgrade', 'copies', 'status')


def make_achievement_form(ses):
    """
    Generate a session-specific form class for achievements that restricts the
    pilots and enemies to the ones assigned to the session.
    """
    class AchForm(forms.ModelForm):
        pilot = forms.ModelChoiceField(queryset=ses.pilots)
        target = forms.ModelChoiceField(queryset=ses.sessionenemy_set, required=False)
        event = forms.ModelChoiceField(queryset=ses.campaign.rulebook.events)


        #def __init__(self, *args, **kwargs):
        #    super().__init__(*args, **kwargs)
        #    self.helper = AchHelper()
            #self.helper.template = 'bootstrap/table_inline_field.html'
            #self.helper.field_template = 'bootstrap4/layout/inline_field.html'

        class Meta:
            model = Achievement
            fields = ('pilot', 'event', 'target', 'turn')

    return AchForm


def make_pilot_upgrade_form(pilot):

    class PilotUpdateForm(forms.ModelForm):
        already_has = pilot.upgrades.values_list('id', flat=True)
        upgrades = forms.ModelMultipleChoiceField(queryset=Upgrade.objects.exclude(id__in=already_has),
                                                  widget=CheckboxSelectMultiple(),
                                                  required=False)
        callsign = forms.CharField(required=False)

        class Meta:
            model = Pilot
            fields = ('callsign', 'upgrades')

    return PilotUpdateForm


class UpgradePurchaseForm(forms.ModelForm):

    class Meta:
        model = Upgrade
        fields = ('id',)



#    def __init__(self, *args, **kwargs):
#        super(BuyUpgradeForm, self).__init__(*args, **kwargs)

#        self.fields["fields"].widget = CheckboxSelectMultiple()
#        self.fields["fields"].queryset = Upgrade.objects.all()
