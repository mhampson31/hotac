from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field, MultiField
from crispy_bootstrap5.bootstrap5 import FloatingField

from .models import EnemyPilot, EnemyAbility, Session, SessionPilot, SessionEnemy, \
                    Pilot, PilotUpgrade, CampaignUpgrade, Campaign
from .fields import GroupedModelChoiceField

from xwtools.models import Upgrade, SlotChoice



class EnemyPilotForm(forms.Form):
    pass
#    level = forms.ChoiceField(EnemyAbility.Level.choices)

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


class CampaignForm(forms.ModelForm):
    prefix = 'campaign'

    class Meta:
        model = Campaign
        fields = ('victory', 'description', 'pool_xp')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Div(
                FloatingField('victory'),
                FloatingField('description'),
                Field('pool_xp')
            )
        )




class SessionForm(forms.ModelForm):
    prefix = 'session'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        #self.helper.form_class = 'form-inline'
        #self.helper.field_template = 'bootstrap4/layout/inline_field.html'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Div(
                FloatingField('date', wrapper_class='col-6'),
                FloatingField('outcome', wrapper_class='col-6')
            )
        )

    class Meta:
        model = Session
        fields = ['date', 'outcome']


SessionPilotFormset = inlineformset_factory(Session,
                                            SessionPilot,
                                            exclude=('pilot', 'ship', 'initiative',),
                                            extra=0)

SessionEnemyFormset = inlineformset_factory(Session,
                                            SessionEnemy,
                                            fields=('killed_by',),
                                            extra=0)


class SPFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.layout = Layout(
            Div(
                FloatingField('status', wrapper_class="col-6 gx-2"),
                FloatingField('bonus', wrapper_class='col-3 gx-2'),
                FloatingField('penalty', wrapper_class='col-3 gx-2'),
                css_class="row mb-1"
            ),
            Div(
                FloatingField('hits', wrapper_class='col-3 gx-2'),
                FloatingField('assists', wrapper_class='col-3 gx-2'),
                FloatingField('guards', wrapper_class='col-3 gx-2'),
                FloatingField('emplacements', wrapper_class='col-3 gx-2'),
                css_class='form-group row mb-1'
            )
        )


class SEFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.layout = Layout(
            Div(
                FloatingField('killed_by', wrapper_class="col")
            )
        )


class PilotUpgradeForm(forms.ModelForm):
    from operator import methodcaller

    upgrade = GroupedModelChoiceField(queryset=CampaignUpgrade.objects.all(),
                                      choices_groupby=methodcaller('get_type_display'))
    copies = forms.IntegerField(min_value=1)
    status = forms.ChoiceField(choices=PilotUpgrade.UStatusChoice.choices)

    class Meta:
        model = PilotUpgrade
        fields = ('upgrade', 'copies', 'status')


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
