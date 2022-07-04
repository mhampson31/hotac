from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth.views import LoginView
from rest_framework.routers import DefaultRouter

from xwtools import views as xwt_views
from campaign import views as campaign_views


xwt_router = DefaultRouter()
xwt_router.register(r'factions', xwt_views.FactionViewSet, basename="factions")
xwt_router.register(r'chassis', xwt_views.ChassisViewSet, basename="chassis")

urlpatterns = [
    #path('login/', LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('_nested_admin/', include('nested_admin.urls')),
    path('admin/', admin.site.urls),


    path('', campaign_views.index, name='index'),
    path('game/', include('campaign.urls', namespace='game')),
    #path('pilot/<int:pk>/', campaign_views.)

    path('chassis/<slug:chassis_slug>/', xwt_views.ship_sheet, name='chassis'),
    path('chassis/<slug:chassis_slug>/ai/', campaign_views.ai_select, name='ai'),
    path('enemy/<int:pk>', campaign_views.EnemyView.as_view(), name='enemy'),
    path('enemy_list/', campaign_views.enemy_list, name='enemy_list'),
    #path('random-enemy', campaign)

    path('api/xwtools/', include(xwt_router.urls))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
