from asset import rest_views
from rest_framework import routers
from django.conf.urls import url, include


router = routers.DefaultRouter()
router.register(r'asset', rest_views.AssetViewSet)
router.register(r'idc', rest_views.IDCViewSet)
router.register(r'userprofile', rest_views.UserProfileViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]
