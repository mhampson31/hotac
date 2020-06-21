from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from xwtools import views as xwt_views
from campaign import views as campaign_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', campaign_views.index, name='index'),
    path('game/', include('campaign.urls', namespace='game')),
    #path('pilot/<int:pk>/update', campaign_views.PilotUpdate.as_view(), name='pilot-update'),

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
