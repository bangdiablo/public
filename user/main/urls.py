from django.urls import path
from . import views

urlpatterns = [

    path('logout/', views.Logout.as_view()),
    path('main/', views.Main.as_view()),
    path('userinfo/', views.UserInfo.as_view()),
]
