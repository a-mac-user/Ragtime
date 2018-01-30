from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^asset/', include('asset.urls')),
    url(r'^api/', include('asset.rest_urls')),
    url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework'))
]
