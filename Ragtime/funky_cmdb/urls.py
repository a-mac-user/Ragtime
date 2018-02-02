from funky_cmdb import views
from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^asset/', include('asset.urls')),
    url(r'^api/', include('asset.rest_urls')),
    url(r'^$', views.index, name="dashboard"),
    url(r'^login.html$', views.acc_login, name='login'),
    url(r'^charts.html$', views.charts, name='charts'),
    url(r'^tables.html$', views.tables, name='tables'),
    url(r'^events.html$', views.events, name='events'),
]
