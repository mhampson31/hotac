from django.urls import include, path
from rest_framework import routers

from . import views

app_name = 'game'

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('pilot/<int:pk>', views.PilotUpdate.as_view(), name='pilot'),
    path('rulebook/<int:pk>', views.RulebookView.as_view(), name='rulebook'),

    path('campaign/<int:pk>', views.CampaignView.as_view(), name='campaign'),
    #path('campaign/<int:pk>/plan', views.CampaignUpdate.as_view(), name='campaign-plan'),

    path('campaign/<int:pk>/plan', views.SessionPlan.as_view(), name='next-mission'),

    path('session/<int:session_id>', views.session_summary, name='session'),
    path('session/<int:pk>/debrief', views.SessionDebrief.as_view(), name='session-debrief'),

    path('profile/', views.player_page, name='player_profile'),
    path('player/<int:player_id>', views.player_page, name="player_update"),

    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

]
