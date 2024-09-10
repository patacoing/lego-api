from django.core.exceptions import ObjectDoesNotExist, BadRequest
from django.db import IntegrityError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, serializers
from rest_framework.decorators import api_view, parser_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.responses import ResponseNotFound, ResponseBadRequest
from .models import Set
from .serializers import SetSerializer, CreateSetSerializer, UpdateSetSerializer, FileUploadSerializer


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

    sets = [
        Set(
            num=row.set_num,
            year=row.year,
            name=row.name,
            num_parts=row.num_parts,
            img_url=row.img_url,
            theme_id=row.theme_id,
        )
        for row in df.itertuples()
    ]

    try:
        Set.objects.bulk_create(sets)
    except IntegrityError:
        return ResponseBadRequest("Set already exists or Theme provided doesn't exist")

    return Response()


class SetListView(APIView):
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
        sets  = Set.objects.all()
        paginator = LimitOffsetPagination()
        result_page = paginator.paginate_queryset(sets, request)

        serializer = SetSerializer(result_page, many=True)

        return Response(serializer.data)

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

        try:
            set_object.save()
        except IntegrityError:
            return ResponseBadRequest("Theme doesn't exist or Num is already in the db")

        return Response(SetSerializer(set_object).data)


class SetDetailView(APIView):
    @staticmethod
    @extend_schema(
        responses={status.HTTP_202_ACCEPTED: SetSerializer},
        operation_id="getSetById",
        summary="Get a set"
    )
    def get(request: Request, pk: int) -> Response:
        try:
            set_object = Set.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return ResponseBadRequest("Set does not exist")

        serializer = SetSerializer(set_object)

        return Response(serializer.data)

    @staticmethod
    @extend_schema(
        responses={status.HTTP_204_NO_CONTENT: None},
        summary="Delete a set"
    )
    def delete(request: Request, pk: int) -> Response:
        try:
            set_object = Set.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return ResponseBadRequest("Set does not exist")

        set_object.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    @extend_schema(
        request=UpdateSetSerializer,
        responses={status.HTTP_202_ACCEPTED: SetSerializer},
        summary="Update a set"
    )
    def patch(request: Request, pk: int) -> Response:
        try:
            set_object = Set.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return ResponseNotFound("Set does not exist")

        serializer = UpdateSetSerializer(set_object, data=request.data)

        if not serializer.is_valid():
            return ResponseBadRequest(serializer.errors)

        set_object = serializer.save()

        try:
            set_object.save()
        except IntegrityError:
            return ResponseBadRequest("Theme doesn't exist or num is already in the db")

        return Response(SetSerializer(set_object).data)
