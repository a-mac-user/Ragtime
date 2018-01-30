from asset import models
from rest_framework import viewsets
from asset.rest_serializers import *


class AssetViewSet(viewsets.ModelViewSet):
    queryset = models.Asset.objects.all()
    serializer_class = AssetSerializer


class IDCViewSet(viewsets.ModelViewSet):
    queryset = models.IDC.objects.all()
    serializer_class = IDCSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all()
    serializer_class = UserProfileSerializer
