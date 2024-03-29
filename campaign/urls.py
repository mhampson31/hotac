from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'game'

router = DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'pilot', views.PilotViewSet)

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

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
