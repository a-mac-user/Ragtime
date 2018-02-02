from asset import rest_views
from rest_framework import routers
from asset import views as asset_views
from django.conf.urls import url, include


router = routers.DefaultRouter()
router.register(r'users', rest_views.UserViewSet)
router.register(r'assets', rest_views.AssetViewSet)
router.register(r'servers', rest_views.ServerViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'asset_list/$', rest_views.AssetList),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^dashboard_data/', asset_views.get_dashboard_data, name="get_dashboard_data"),
]
