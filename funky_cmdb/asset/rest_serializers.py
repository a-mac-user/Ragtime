from asset import models
from rest_framework import serializers


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Asset
        depth = 2
        fields = ('sn', 'name', 'status', 'asset_type', 'idc')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ('email', 'name')


class IDCSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ('name', )
