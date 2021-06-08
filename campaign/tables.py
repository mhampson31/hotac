import django_tables2 as tables
from .models import Session


class SessionTable(tables.Table):
    class Meta:
        model = Session
        fields = ('pilot__callsign', 'event__short_desc', 'total', 'xp')
        template_name = 'django_tables2/bootstrap.html'
