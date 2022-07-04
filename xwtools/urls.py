from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'xwtools'

router = DefaultRouter()
router.register(r'factions', views.FactionViewSet, basename="factions")
router.register(r'chassis', views.ChassisViewSet, basename="chassis")

urlpatterns = [
    path('api/', include(router.urls)),
]
