from django.urls import path

from . import views

app_name = "modelsdemo"
urlpatterns = [
    path("", views.index, name="index"),
]
