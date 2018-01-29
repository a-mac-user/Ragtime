from asset import views
from django.conf.urls import url

urlpatterns = [
    url(r'report/asset_with_no_asset_id/$', views.asset_with_no_asset_id),
    url(r'new_assets/approval/$', views.new_assets_approval, name='new_assets_approval'),
]
