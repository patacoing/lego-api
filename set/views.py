from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, serializers
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, AND, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.responses import ResponseBadRequest
from .serializers import SetSerializer, CreateSetSerializer, UpdateSetSerializer, FileUploadSerializer
from .services import SetService


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

    return SetService.bulk_import(df)


class SetListView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    @extend_schema(
        parameters=[
            OpenApiParameter(name="limit", location=OpenApiParameter.QUERY, type=OpenApiTypes.INT, default=10),
            OpenApiParameter(name="offset", location=OpenApiParameter.QUERY, type=OpenApiTypes.INT, default=0),
        ],
        responses={status.HTTP_202_ACCEPTED: SetSerializer},
        operation_id="getPaginatedSets",
        summary="Get paginated sets"
    )
    def get(request: Request) -> Response:
        return SetService.get_paginated(request)

    @staticmethod
    @extend_schema(
        request=CreateSetSerializer,
        responses={status.HTTP_201_CREATED: SetSerializer},
        summary="Create a set"
    )
    def post(request: Request) -> Response:
        serializer = CreateSetSerializer(data=request.data)

        if not serializer.is_valid():
            return ResponseBadRequest(serializer.errors)

        set_object = serializer.save()

        return SetService.create(set_object)


class SetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    @extend_schema(
        responses={status.HTTP_202_ACCEPTED: SetSerializer},
        operation_id="getSetById",
        summary="Get a set"
    )
    def get(request: Request, pk: int) -> Response:
        return SetService.get(pk)

    @staticmethod
    @extend_schema(
        responses={status.HTTP_204_NO_CONTENT: None},
        summary="Delete a set"
    )
    def delete(request: Request, pk: int) -> Response:
        return SetService.delete(pk)

    @staticmethod
    @extend_schema(
        request=UpdateSetSerializer,
        responses={status.HTTP_202_ACCEPTED: SetSerializer},
        summary="Update a set"
    )
    def patch(request: Request, pk: int) -> Response:
        return SetService.update(request, pk)
