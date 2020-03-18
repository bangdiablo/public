from django.urls import path
from . import views

urlpatterns = [

    path('connect_to_google/', views.google_login),
    path('connect_to_google_drive/', views.callback),
    path('google_drive/', views.google_drive),
    path('downloadFile/', views.downloadFile.as_view()),
    path('deleteTempPath/', views.deleteTempPath.as_view()),
    path('get_storage_service/', views.get_storage_service.as_view()),
    path('getFolderList/', views.get_folder_list.as_view()),
    path('disconnected_google_drive/', views.disconnected_google_drive.as_view()),
    path('delete/', views.delete.as_view()),

]
