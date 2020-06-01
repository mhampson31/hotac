from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from xwtools import views as xwt_views
from campaign import views as campaign_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', campaign_views.index, name='index'),
    path('session/<int:session_id>', campaign_views.session_summary, name='session'),
    path('session/<int:session_id>/plan', campaign_views.session_plan, name='session-plan'),
    path('pilot/<int:pilot_id>', campaign_views.pilot_sheet, name='pilot'),
    path('campaign/<int:pk>', campaign_views.CampaignView.as_view(), name='campaign'),
    path('game/<int:pk>', campaign_views.GameView.as_view(), name='game'),
    path('chassis/<slug:chassis_slug>/', xwt_views.ship_sheet, name='chassis'),
    path('chassis/<slug:chassis_slug>/ai/', campaign_views.ai_select, name='ai'),
    path('enemy/<int:pk>', campaign_views.EnemyView.as_view(), name='enemy'),
    path('enemy_list/', campaign_views.enemy_list, name='enemy_list'),
    #path('random-enemy', campaign)
    path('chaining/', include('smart_selects.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
