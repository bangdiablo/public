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
from django.urls import path, include

urlpatterns = [

    # before_login
    path('before_login/', include('reseller.before_login.urls')),

    # main
    path('main/', include('reseller.main.urls')),

    # reseller
    path('reseller/', include('reseller.reseller.urls')),

    # account
    path('account/', include('reseller.account.urls')),

    # license
    path('license/', include('reseller.license.urls')),

    # plan
    path('plan/', include('reseller.plan.urls')),

    # report
    path('plan/', include('reseller.plan.urls')),

    # setting
    path('plan/', include('reseller.plan.urls')),
]
