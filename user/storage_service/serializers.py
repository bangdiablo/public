from rest_framework import serializers

from .models import Googledrivefiles, Googledrivesettings
from ..models import BoxFile


class GoogleDriveFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Googledrivefiles
        fields = '__all__'


class BoxFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxFile
        fields = '__all__'


class GoogleDriveSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Googledrivesettings
        fields = '__all__'
