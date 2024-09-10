from django.core.exceptions import ObjectDoesNotExist, BadRequest
from django.db import IntegrityError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, serializers
from rest_framework.decorators import api_view, parser_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
import pandas as pd
import numpy as np
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from theme.models import Theme
from theme.serializers import ThemeSerializer, CreateThemeSerializer, UpdateThemeSerializer, FileUploadSerializer
from utils.responses import ResponseNotFound, ResponseBadRequest


@extend_schema(
    request=FileUploadSerializer,
    responses={status.HTTP_200_OK: None},
    summary="Bulk import"
)
@api_view(['POST'])
@parser_classes([MultiPartParser])
def bulk_import(request: Request) -> Response:
    serializer = FileUploadSerializer(data=request.data)

    if not serializer.is_valid():
        return ResponseBadRequest(serializer.errors)

    try:
        df = serializer.save()
    except serializers.ValidationError as e:
        return ResponseBadRequest(e.detail)

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


class ThemeListView(APIView):
    @staticmethod
    @extend_schema(
        parameters=[
            OpenApiParameter(name="limit", location=OpenApiParameter.QUERY, type=OpenApiTypes.INT, default=10),
            OpenApiParameter(name="offset", location=OpenApiParameter.QUERY, type=OpenApiTypes.INT, default=0),
        ],
        responses={status.HTTP_202_ACCEPTED: ThemeSerializer},
        operation_id="getPaginatedThemes",
        summary="Get paginated themes"
    )
    def get(request: Request) -> Response:
        themes  = Theme.objects.all()
        paginator = LimitOffsetPagination()
        result_page = paginator.paginate_queryset(themes, request)

        serializer = ThemeSerializer(result_page, many=True)

        return Response(serializer.data)

    @staticmethod
    @extend_schema(
        request=CreateThemeSerializer,
        responses={status.HTTP_201_CREATED: ThemeSerializer},
        summary="Create a theme"
    )
    def post(request: Request) -> Response:
        serializer = CreateThemeSerializer(data=request.data)

        if not serializer.is_valid():
            return ResponseBadRequest(serializer.errors)

        theme = serializer.save()

        try:
            theme.save()
        except IntegrityError:
            return ResponseBadRequest("Parent theme doesn't exist")

        return Response(ThemeSerializer(theme).data)


class ThemeDetailView(APIView):
    @staticmethod
    @extend_schema(
        responses={status.HTTP_202_ACCEPTED: ThemeSerializer},
        operation_id="getThemeById",
        summary="Get a theme"
    )
    def get(request: Request, pk: int) -> Response:
        try:
            theme = Theme.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return ResponseNotFound("Theme doesn't exist")

        serializer = ThemeSerializer(theme)

        return Response(serializer.data)

    @staticmethod
    @extend_schema(
        responses={status.HTTP_204_NO_CONTENT: None},
        summary="Delete a theme"
    )
    def delete(request: Request, pk: int) -> Response:
        try:
            theme = Theme.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return ResponseNotFound("Theme doesn't exist")

        theme.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    @extend_schema(
        request=UpdateThemeSerializer,
        responses={status.HTTP_202_ACCEPTED: ThemeSerializer},
        summary="Update a theme"
    )
    def patch(request: Request, pk: int) -> Response:
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