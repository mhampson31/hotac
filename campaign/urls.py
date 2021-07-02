from django.urls import path

from . import views

app_name = 'game'

urlpatterns = [
    path('pilot/<int:pk>', views.PilotUpdate.as_view(), name='pilot'),
    path('rulebook/<int:pk>', views.RulebookView.as_view(), name='rulebook'),

    path('campaign/<int:pk>', views.CampaignView.as_view(), name='campaign'),
    #path('campaign/<int:pk>/plan', views.CampaignUpdate.as_view(), name='campaign-plan'),

    path('campaign/<int:pk>/plan', views.SessionPlan.as_view(), name='next-mission'),

    path('session/<int:session_id>', views.session_summary, name='session'),
    path('session/<int:pk>/debrief', views.SessionDebrief.as_view(), name='session-debrief'),

]
