import numpy as np
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from theme.models import Theme
from theme.serializers import ThemeSerializer, UpdateThemeSerializer
from utils.responses import ResponseBadRequest, ResponseNotFound


class ThemeService:
    @staticmethod
    def bulk_import(df: pd.DataFrame) -> Response:
        df = df.replace(np.nan, None)

        df_themes_to_add = df[df["parent_id"].isna()]
        themes = [Theme(id=row.id, name=row.name, parent_id=row.parent_id) for row in df_themes_to_add.itertuples()]
        df = df.dropna()
        df = df.astype({"id": int, "parent_id": int})

        while df_themes_to_add.shape[0] > 0:
            df_themes_to_add = df[df["parent_id"].isin(df_themes_to_add["id"])]
            themes.extend([Theme(id=row.id, name=row.name, parent_id=row.parent_id) for row in
                           df_themes_to_add.itertuples()])

        try:
            Theme.objects.bulk_create(themes)
        except IntegrityError:
            return ResponseBadRequest("Theme already exists")

        return Response({"detail": "Successfully imported"})

    @staticmethod
    def get_paginated(request: Request) -> Response:
        themes = Theme.objects.all()
        paginator = LimitOffsetPagination()
        result_page = paginator.paginate_queryset(themes, request)

        serializer = ThemeSerializer(result_page, many=True)

        return Response(serializer.data)

    @staticmethod
    def create(theme: Theme) -> Response:
        try:
            theme.save()
        except IntegrityError:
            return ResponseBadRequest("Parent theme doesn't exist")

        return Response(ThemeSerializer(theme).data)

    @staticmethod
    def get(pk: int) -> Response:
        try:
            theme = Theme.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return ResponseNotFound("Theme doesn't exist")

        serializer = ThemeSerializer(theme)

        return Response(serializer.data)

    @staticmethod
    def delete(pk: int) -> Response:
        try:
            theme = Theme.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return ResponseNotFound("Theme doesn't exist")

        theme.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def update(request: Request, pk: int) -> Response:
        try:
            theme = Theme.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return ResponseNotFound("Theme doesn't exist")

        serializer = UpdateThemeSerializer(theme, data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        theme = serializer.save()

        try:
            theme.save()
        except IntegrityError:
            return ResponseBadRequest("Theme doesn't exist")

        return Response(ThemeSerializer(theme).data)