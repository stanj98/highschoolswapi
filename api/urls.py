from django.urls import path
from api import views

urlpatterns = [
    path('', views.swapi_research),
    path('<str:resource>/', views.swapi_research),
    path('<str:resource>/<int:obj_id>/', views.swapi_research),
    path('<str:resource>/<int:obj_id>/<str:summarize>/', views.swapi_research),
]