from operator import methodcaller

from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field, MultiField
from crispy_bootstrap5.bootstrap5 import FloatingField

from .models import EnemyPilot, EnemyAbility, Session, SessionPilot, SessionEnemy, \
                    Pilot, PilotUpgrade, Campaign
from .fields import GroupedModelChoiceField

from xwtools.models import SlotChoice, Card


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
                FloatingField('card', wrapper_class='col-4'),

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


AddSessionPilotFormset = inlineformset_factory(Session, SessionPilot,
                                            fields=('pilot', 'ship', 'initiative',),
                                            extra=1)


SessionPilotFormset = inlineformset_factory(Session, SessionPilot,
                                            exclude=('pilot', 'ship', 'initiative',),
                                            extra=0)

SessionEnemyFormset = inlineformset_factory(Session, SessionEnemy,
                                            fields=('killed_by',),
                                            extra=0)


class SessionPlanForm(forms.ModelForm):
    prefix = 'session'

    class Meta:
        model = Session
        fields = ['mission', 'campaign']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(kwargs)
        self.fields['campaign'].widget = forms.HiddenInput()
        self.fields['mission'].widget = forms.RadioSelect()
        self.fields['mission'].empty_label = None
        campaign = kwargs.get('initial')['campaign']
        self.fields['mission'].queryset = campaign.deck.filter(id__in=campaign.deck_draw)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.layout = Layout(
            Div(
                Field('mission', wrapper_class='card-body'),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))



class SessionPilotHelper(FormHelper):
    """
    SessionPilot formset helper for SessionCreate
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False


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


class AddUpgrade(forms.ModelForm):
    prefix = 'add_upgrade'
    card = GroupedModelChoiceField(queryset=Card.objects.filter(description__isnull=False),
                                      choices_groupby=methodcaller('get_type_display'))

    class Meta:
        model = PilotUpgrade
        fields = ['card', 'status', 'pilot']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget = forms.HiddenInput()
        self.fields['pilot'].widget = forms.HiddenInput()
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.layout = Layout(
            FloatingField('card', wrapper_class="col-2"),
        )
        self.helper.add_input(Submit('submit', 'Purchase'))
