"""usersite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    # before_login
    path('before_login/', include('user.before_login.urls')),

    # main
    path('main/', include('user.main.urls')),

    # header
    path('header/', include('user.header.urls')),

    # home
    path('home/', include('user.home.urls')),

    # my_file
    path('my_file/', include('user.my_file.urls')),

    # recycle_bin
    path('recycle_bin/', include('user.recycle_bin.urls')),

    # cloud_drive
    path('cloud_drive/', include('user.cloud_drive.urls')),

    # favorite
    path('favorite/', include('user.favorite.urls')),

    # connected_device
    path('connected_device/', include('user.connected_device.urls')),

    # storage_service
    path('storage_service/', include('user.storage_service.urls')),

    # management
    path('management/', include('user.management.urls')),

]
