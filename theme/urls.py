from django.urls import path
from theme import views

urlpatterns = [
    path('bulk', views.bulk_import),
    path('', views.ThemeListView.as_view()),
    path('<int:pk>', views.ThemeDetailView.as_view())
]