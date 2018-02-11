from asset import models
from asset.myauth import UserProfile
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('url', 'name', 'email')


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Asset
        depth = 2
        fields = ('name', 'sn', 'server', 'networkdevice')


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Server
