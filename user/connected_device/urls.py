from django.urls import path
from . import views

urlpatterns = [

    path('device_name', views.DeviceName.as_view()),
    path('connected-device-data', views.GetData.as_view()),
    path('folder-file', views.GetFolderFile.as_view()),
    path('version', views.GetVersionInfo.as_view()),
    path('parent', views.GetParent.as_view()),
    path('category', views.GetCategory.as_view()),
    path('favorite', views.FavoriteRegistration.as_view()),
    path('favorite-del', views.FavoriteRegistrationDel.as_view()),

]
