from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('problems', views.problem_list, name='problem_list'),
    path('problems/<int:pk>/edit/', views.problem_edit, name='problem_edit'),
    path('test/<int:pk>', views.test, name='test'),
]