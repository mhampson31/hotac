from django.contrib import admin
from django.urls import path

from campaign import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('session/<int:session_id>', views.session_summary, name='session'),
    path('pilot/<int:pilot_id>', views.pilot_sheet, name='pilot'),
    path('campaign/<int:pk>', views.CampaignView.as_view(), name='campaign')
]
