import pandas as pd
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from set.models import Set
from set.serializers import SetSerializer, UpdateSetSerializer
from utils.responses import ResponseBadRequest


class SetService:
    @staticmethod
    def bulk_import(df: pd.DataFrame) -> Response:
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

    @staticmethod
    def get_paginated(request: Request) -> Response:
        sets = Set.objects.all()
        paginator = LimitOffsetPagination()
        result_page = paginator.paginate_queryset(sets, request)

        serializer = SetSerializer(result_page, many=True)

        return Response(serializer.data)

    @staticmethod
    def create(set_object: Set) -> Response:
        try:
            set_object.save()
        except IntegrityError:
            return ResponseBadRequest("Theme doesn't exist or Num is already in the db")

        return Response(SetSerializer(set_object).data)

    @staticmethod
    def get(pk: int) -> Response:
        set_object = get_object_or_404(Set, pk=pk)

        serializer = SetSerializer(set_object)

        return Response(serializer.data)

    @staticmethod
    def delete(pk: int) -> Response:
        set_object = get_object_or_404(Set, pk=pk)

        set_object.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def update(request: Request, pk: int) -> Response:
        set_object = get_object_or_404(Set, pk=pk)

        serializer = UpdateSetSerializer(set_object, data=request.data)

        if not serializer.is_valid():
            return ResponseBadRequest(serializer.errors)

        set_object = serializer.save()

        try:
            set_object.save()
        except IntegrityError:
            return ResponseBadRequest("Theme doesn't exist or num is already in the db")

        return Response(SetSerializer(set_object).data)