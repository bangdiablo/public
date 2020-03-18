from django.urls import path
from . import views

urlpatterns = [

    path('favorite_data', views.GetFavoriteData.as_view()),


]
