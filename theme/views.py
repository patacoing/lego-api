from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, serializers
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from theme.serializers import ThemeSerializer, CreateThemeSerializer, UpdateThemeSerializer, FileUploadSerializer
from theme.services import ThemeService
from utils.responses import ResponseBadRequest


@extend_schema(
    request=FileUploadSerializer,
    responses={status.HTTP_200_OK: None},
    summary="Bulk import"
)
@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated, IsAdminUser])
def bulk_import(request: Request) -> Response:
    serializer = FileUploadSerializer(data=request.data)

    if not serializer.is_valid():
        return ResponseBadRequest(serializer.errors)

    try:
        df = serializer.save()
    except serializers.ValidationError as e:
        return ResponseBadRequest(e.detail)

    return ThemeService.bulk_import(df)


class ThemeListView(APIView):
    permission_classes = [IsAuthenticated]

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
        return ThemeService.get_paginated(request)

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

        return ThemeService.create(theme)


class ThemeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    @extend_schema(
        responses={status.HTTP_202_ACCEPTED: ThemeSerializer},
        operation_id="getThemeById",
        summary="Get a theme"
    )
    def get(request: Request, pk: int) -> Response:
        return ThemeService.get(pk)

    @staticmethod
    @extend_schema(
        responses={status.HTTP_204_NO_CONTENT: None},
        summary="Delete a theme"
    )
    def delete(request: Request, pk: int) -> Response:
        return ThemeService.delete(pk)

    @staticmethod
    @extend_schema(
        request=UpdateThemeSerializer,
        responses={status.HTTP_202_ACCEPTED: ThemeSerializer},
        summary="Update a theme"
    )
    def patch(request: Request, pk: int) -> Response:
        return ThemeService.update(request, pk)