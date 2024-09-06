from django.urls import include, path

urlpatterns = [
    path("themes/", include("theme.urls")),
    path("sets/", include("set.urls")),
]
