from functools import partial
from typing import Union
from django.urls.resolvers import URLPattern, URLResolver

urlpatterns: list[partial[Union[URLResolver, URLPattern]]] = []