import django_tables2 as tables
from .models import Session, Achievement


class SessionTable(tables.Table):
    class Meta:
        model = Session
        fields = ('pilot__callsign', 'event__short_desc', 'total', 'xp')
        template_name = 'django_tables2/bootstrap.html'


class AchievementTable(tables.Table):
    pilot = tables.Column(accessor='pilot__callsign')
    event = tables.Column(accessor='event__short_desc')
    total = tables.Column()
    xp = tables.Column(footer=lambda table: sum(x['xp'] for x in table.data))
    class Meta:
        template_name = 'django_tables2/semantic.html'
        exclude = ('pilot',)