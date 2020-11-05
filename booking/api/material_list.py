from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r

from booking.models import Material
from booking.serializers import MaterialSerializer


class MaterialList(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    renderer_classes = (r.CSVRenderer,) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
