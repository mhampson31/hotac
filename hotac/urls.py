from django.contrib import admin
from django.urls import path, include

from xwtools import views as xwt_views
from campaign import views as campaign_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', campaign_views.index, name='index'),
    path('session/<int:session_id>', campaign_views.session_summary, name='session'),
    path('pilot/<int:pilot_id>', campaign_views.pilot_sheet, name='pilot'),
    path('campaign/<int:pk>', campaign_views.CampaignView.as_view(), name='campaign'),
    path('ses/<int:session_id>', campaign_views.old_session_summary, name='old_ses'),
    path('ship/<slug:ship_slug>/', xwt_views.ship_sheet, name='ship'),
    path('ship/<slug:ship_slug>/ai/', campaign_views.ai_select, name='ai'),
    path('chaining/', include('smart_selects.urls')),
]
