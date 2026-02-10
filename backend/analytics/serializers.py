from rest_framework import serializers
from .models import UploadRecord


class UploadRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadRecord
        fields = ['id', 'file_name', 'uploaded_at', 'summary']
