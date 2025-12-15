from rest_framework import serializers
from .models import App

class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ('id', 'name', 'repo_url', 'subdomain', 'status', 'created_at', 'updated_at', 'buildnumber', 'build_file')
        read_only_fields = ('id', 'created_at', 'updated_at', 'buildnumber')