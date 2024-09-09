from django.urls import path
from set import views


urlpatterns = [
    path("bulk/", views.bulk_import),
    path('', views.SetListView.as_view()),
    path('<int:pk>', views.SetDetailView.as_view())
]