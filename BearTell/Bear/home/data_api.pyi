from rest_framework import serializers
from .models import category_parent, category_child, analyze_type, sensor_name, data_source

class CategorySerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='name')

    class Meta:
        model = category_parent
        fields = ("id", "text")

class SubCategorySerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='name')

    class Meta:
        model = category_child
        fields = ("id", "text")

class SensorNameSerializer(serializers.ModelSerializer):
    text_name = serializers.CharField(source='key_word')

    class Meta:
        model = sensor_name
        fields = ("id", "text_name")

class AnalyzeTypeSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='name')

    class Meta:
        model = analyze_type
        fields = ("id", "text")

class DataSourceSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='name')

    class Meta:
        model = data_source
        fields = ["id", "text", "ip","kimlik"]
