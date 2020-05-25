from django import forms
from .models import EnemyPilot, EnemyAbility

class EnemyPilotForm(forms.Form):
    pass
#    level = forms.ChoiceField(EnemyAbility.Level.choices)
