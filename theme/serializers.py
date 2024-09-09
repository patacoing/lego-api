from typing import Union
from rest_framework import serializers

from theme.models import Theme


class ThemeSerializer(serializers.Serializer):
    name = serializers.CharField()
    parent_id = serializers.IntegerField()
    id = serializers.IntegerField()


class CreateThemeSerializer(serializers.Serializer):
    name = serializers.CharField()
    parent_id = serializers.IntegerField(required=False, allow_null=True, default=None)

    def create(self, validated_data: dict[str, Union[str, int]]) -> Theme:
        return Theme(**validated_data)


class UpdateThemeSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True, default=None)

    def update(self, instance: Theme, validated_data: dict[str, Union[str, int]]) -> Theme:
        instance.name = validated_data.get('name', instance.name)
        instance.parent_id = validated_data.get('parent_id', instance.parent_id)

        return instance
