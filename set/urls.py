from django.urls import path
from set import views


urlpatterns = [
    path("bulk/", views.bulk_import)
]