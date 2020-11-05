from rest_framework import serializers
from sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField

from booking.models import Material, MaterialImage


class MaterialImageSerializer(serializers.ModelSerializer):
    thumbnail = HyperlinkedSorlImageField(
        "32x32", options={}, source="image", read_only=True
    )

    class Meta:
        model = MaterialImage
        fields = ["thumbnail"]


class MaterialSerializer(serializers.ModelSerializer):
    catalogUrl = serializers.CharField(source="get_catalog_modal_url", read_only=True)
    categories = serializers.StringRelatedField(many=True, read_only=True)
    images = MaterialImageSerializer(many=True, read_only=True)

    class Meta:
        model = Material
        fields = ["id", "name", "categories", "catalogUrl", "images"]
