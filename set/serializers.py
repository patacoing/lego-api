from typing import Union
from rest_framework import serializers

from set.models import Set


class SetSerializer(serializers.Serializer):
    num = serializers.CharField()
    name = serializers.CharField()
    year = serializers.IntegerField()
    num_parts = serializers.IntegerField()
    img_url = serializers.URLField()
    theme_id = serializers.IntegerField()
    id = serializers.IntegerField()


class CreateSetSerializer(serializers.Serializer):
    num = serializers.CharField()
    name = serializers.CharField()
    year = serializers.IntegerField()
    num_parts = serializers.IntegerField()
    img_url = serializers.URLField()
    theme_id = serializers.IntegerField()

    def create(self, validated_data: dict[str, Union[str, int]]) -> Set:
        return Set(**validated_data)


class UpdateSetSerializer(serializers.Serializer):
    num = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    year = serializers.IntegerField(required=False)
    num_parts = serializers.IntegerField(required=False)
    img_url = serializers.URLField(required=False)
    theme_id = serializers.IntegerField(required=False)

    def update(self, instance: Set, validated_data: dict[str, Union[str, int]]) -> Set:
        instance.name = validated_data.get('name', instance.name)
        instance.year = validated_data.get('year', instance.year)
        instance.num_parts = validated_data.get('num_parts', instance.num_parts)
        instance.img_url = validated_data.get('img_url', instance.img_url)
        instance.num = validated_data.get('num', instance.num)
        instance.theme_id = validated_data.get('theme_id', instance.theme_id)

        return instance
