from django.core.exceptions import ObjectDoesNotExist, BadRequest
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
import pandas as pd
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Set
from .serializers import SetSerializer, CreateSetSerializer, UpdateSetSerializer


@api_view(['POST'])
@parser_classes([MultiPartParser])
def bulk_import(request: Request) -> HttpResponse:
    files = [uploaded_file.file for uploaded_file in request.FILES.values()]

    if len(files) != 1:
        return HttpResponseBadRequest("Need only 1 file")

    file, = files

    df = pd.read_csv(file)

    if not {"set_num", "year", "name", "theme_id", "num_parts", "img_url"}.issubset(df.columns):
        return HttpResponseBadRequest("Columns must contain id, parent_id and name")

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
        return HttpResponseBadRequest("Set already exists or Theme provided doesn't exist")

    return HttpResponse("Successfully imported")


class SetListView(APIView):
    @staticmethod
    def get(request: Request) -> Response:
        sets  = Set.objects.all()
        paginator = LimitOffsetPagination()
        result_page = paginator.paginate_queryset(sets, request)

        serializer = SetSerializer(result_page, many=True)

        return Response(serializer.data)

    @staticmethod
    def post(request: Request) -> Response:
        serializer = CreateSetSerializer(data=request.data)

        if not serializer.is_valid():
            raise BadRequest(serializer.errors)

        set_object = serializer.save()

        try:
            set_object.save()
        except IntegrityError:
            raise BadRequest("Theme doesn't exist or Num is already in the db")

        return Response(SetSerializer(set_object).data)


class SetDetailView(APIView):
    @staticmethod
    def get(request: Request, pk: int) -> Response:
        try:
            set_object = Set.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = SetSerializer(set_object)

        return Response(serializer.data)

    @staticmethod
    def delete(request: Request, pk: int) -> Response:
        try:
            set_object = Set.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise NotFound()

        set_object.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def patch(request: Request, pk: int) -> Response:
        try:
            set_object = Set.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = UpdateSetSerializer(set_object, data=request.data)

        if not serializer.is_valid():
            raise BadRequest(serializer.errors)

        set_object = serializer.save()

        try:
            set_object.save()
        except IntegrityError:
            raise BadRequest("Theme doesn't exist or num is already in the db")

        return Response(SetSerializer(set_object).data)
