from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
import pandas as pd
from rest_framework.request import Request

from .models import Set


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
