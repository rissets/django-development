from django.urls import path

from . import views

app_name = "projects"
urlpatterns = [
    path("", views.project_list, name="list"),
    path("new/", views.project_form, name="create"),
    path("<int:pk>/", views.project_detail, name="detail"),
    path("<int:pk>/edit/", views.project_form, name="edit"),
    path("<int:pk>/activate/", views.project_transition, {"target": "active"}, name="activate"),
    path("<int:pk>/archive/", views.project_transition, {"target": "archived"}, name="archive"),
]
