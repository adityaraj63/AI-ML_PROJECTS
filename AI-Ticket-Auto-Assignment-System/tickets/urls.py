from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('history/', views.ticket_history, name='ticket_history'),
]
