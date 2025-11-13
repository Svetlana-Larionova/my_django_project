from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
]