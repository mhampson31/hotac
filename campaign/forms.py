from django import forms

from .models import EnemyPilot, EnemyAbility, Session, Pilot, Achievement

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class EnemyPilotForm(forms.Form):
    pass
#    level = forms.ChoiceField(EnemyAbility.Level.choices)


def make_achievement_form(ses):
    """
    Generate a session-specific form class for achievements that restricts the
    pilots and enemies to the ones assigned to the session.
    """
    class AchForm(forms.ModelForm):
        pilot = forms.ModelChoiceField(queryset=ses.pilots)
        target = forms.ModelChoiceField(queryset=ses.enemies)
        event = forms.ModelChoiceField(queryset=ses.game.campaign.events)


        class Meta:
            model = Achievement
            fields = ('pilot', 'event', 'target', 'turn')

    return AchForm


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
