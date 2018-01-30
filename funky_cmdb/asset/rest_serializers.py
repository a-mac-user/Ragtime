from asset import models
from rest_framework import serializers


class AssetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Asset
        fields = ('sn', 'name', 'status', 'asset_type')
