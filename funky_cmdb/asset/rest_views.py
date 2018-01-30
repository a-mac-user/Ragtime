from asset import models
from rest_framework import viewsets
from asset.rest_serializers import AssetSerializer


class AssetViewSet(viewsets.ModelViewSet):
    queryset = models.Asset.objects.all()
    serializer_class = AssetSerializer
