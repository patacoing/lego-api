from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
import pandas as pd
import numpy as np
from rest_framework.request import Request

from theme.models import Theme


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
