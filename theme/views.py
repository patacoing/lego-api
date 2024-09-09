from django.core.exceptions import ObjectDoesNotExist, BadRequest
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound, HttpResponseGone
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
import pandas as pd
import numpy as np
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from theme.models import Theme
from theme.serializers import ThemeSerializer, CreateThemeSerializer, UpdateThemeSerializer


@api_view(['POST'])
@parser_classes([MultiPartParser])
def bulk_import(request: Request) -> HttpResponse:
    files = [uploaded_file.file for uploaded_file in request.FILES.values()]

    if len(files) != 1:
        return HttpResponseBadRequest("Need only 1 file")

    file, = files

    df = pd.read_csv(file)

    if not {"id", "parent_id", "name"}.issubset(df.columns):
        return HttpResponseBadRequest("Columns must contain id, parent_id and name")

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
        return HttpResponseBadRequest("Theme already exists")

    return HttpResponse("Successfully imported")


class ThemeListView(APIView):
    @staticmethod
    def get(request: Request) -> Response:
        themes  = Theme.objects.all()
        paginator = LimitOffsetPagination()
        result_page = paginator.paginate_queryset(themes, request)

        serializer = ThemeSerializer(result_page, many=True)

        return Response(serializer.data)

    @staticmethod
    def post(request: Request) -> Response:
        serializer = CreateThemeSerializer(data=request.data)

        if not serializer.is_valid():
            raise BadRequest(serializer.errors)

        theme = serializer.save()

        try:
            theme.save()
        except IntegrityError:
            raise BadRequest("Parent theme doesn't exist")

        return Response(ThemeSerializer(theme).data)


class ThemeDetailView(APIView):
    @staticmethod
    def get(request: Request, pk: int) -> Response:
        try:
            theme = Theme.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = ThemeSerializer(theme)

        return Response(serializer.data)

    @staticmethod
    def delete(request: Request, pk: int) -> Response:
        try:
            theme = Theme.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise NotFound()

        theme.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def patch(request: Request, pk: int) -> Response:
        try:
            theme = Theme.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = UpdateThemeSerializer(theme, data=request.data)

        if not serializer.is_valid():
            raise BadRequest(serializer.errors)

        theme = serializer.save()

        try:
            theme.save()
        except IntegrityError:
            raise BadRequest("Theme doesn't exist")

        return Response(ThemeSerializer(theme).data)