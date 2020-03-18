from rest_framework import serializers

from ..models import BoxUserstorage
from ..models import BoxFile


class BoxUserStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxUserstorage
        fields = '__all__'
