from django.urls import path
from . import views

app_name = 'crud'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('<int:id>/', views.task_detail, name='task_detail'),
    path('<int:id>/update/', views.task_update, name='task_update'),
    path('<int:id>/delete/', views.task_delete, name='task_delete'),
]