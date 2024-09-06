from django.urls import path
from theme import views

urlpatterns = [
    path('bulk', views.bulk_import),
]