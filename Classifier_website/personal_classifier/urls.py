from django.urls import path

from . import views

app_name = 'personal_classifier'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_collection, name='upload_collection'),
    path('search/', views.search_collection.as_view(), name='search_collection'),
    path('search/<str:email_id>/', views.detail, name='detail'),
    path('graph/', views.graph_collection, name='graph_collection'),
    path('search/user/<str:user_id>/', views.user_email, name='user_id'),
]