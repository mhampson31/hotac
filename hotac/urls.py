from django.contrib import admin
from django.urls import path, include

from campaign import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('session/<int:session_id>', views.session_summary, name='session'),
    path('pilot/<int:pilot_id>', views.pilot_sheet, name='pilot'),
    path('campaign/<int:pk>', views.CampaignView.as_view(), name='campaign'),
    path('ses/<int:session_id>', views.old_session_summary, name='old_ses'),
    path('ship/<slug:ship_slug>/', views.ship_sheet, name='ship'),
    path('ship/<slug:ship_slug>/ai/', views.ai_select, name='ai'),
    path('chaining/', include('smart_selects.urls')),
]
