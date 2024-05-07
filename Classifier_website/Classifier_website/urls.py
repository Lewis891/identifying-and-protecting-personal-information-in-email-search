"""Classifier_website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from personal_classifier import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('personal_classifier/', include('personal_classifier.urls')),
    path('', views.index, name='index'),
    path('upload/', views.upload_collection, name='upload_collection'),
    path('search/', views.search_collection.as_view(), name='search_collection'),
    path('search/<str:email_id>/', views.detail, name='detail'),
    path('graph/', views.graph_collection, name='graph_collection'),
    path('search/user/<str:user_id>/', views.user_email, name='user_id'),
]
