from asset import views
from asset import rest_views
from rest_framework import routers
from django.conf.urls import url, include


router = routers.DefaultRouter()
router.register(r'users', rest_views.AssetViewSet)

urlpatterns = [
    url(r'api', include(router.urls)),
    url(r'report/asset_with_no_asset_id/$', views.asset_with_no_asset_id),
    url(r'new_assets/approval/$', views.new_assets_approval, name='new_assets_approval'),
]
