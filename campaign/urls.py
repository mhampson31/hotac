from django.urls import path

from . import views

app_name = 'game'

urlpatterns = [
    path('pilot/<int:pk>', views.pilot_sheet, name='pilot'),
    path('rulebook/<int:pk>', views.RulebookView.as_view(), name='rulebook'),
    path('campaign/<int:pk>', views.CampaignView.as_view(), name='campaign'),
    path('session/<int:session_id>', views.session_summary, name='session'),
    path('session/<int:session_id>/plan', views.session_plan, name='session-plan'),

]