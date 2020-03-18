from django.urls import path
from . import views

urlpatterns = [
    path('', views.Resellers.as_view()),
]