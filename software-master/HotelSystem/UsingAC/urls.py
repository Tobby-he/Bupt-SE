from django.urls import path
from . import views

urlpatterns = [
    path('api/temperature/', views.handleTemperature, name='handle_temperature'),
    path('api/power/', views.handle_power, name='handle_power'),
    path('api/fan-speed/', views.handle_fan_speed, name='handle_fan_speed'),
    path('api/test/', views.Test, name='test'),
    path('api/room_status/', views.get_rooms_status, name='get_rooms_status'),
    path('api/register-customer/', views.register_customer, name='register_customer'),
    path('api/check-room-state/', views.check_room_state, name='check_room_state'),
    path('api/create-accommodation-order/', views.create_accommodation_order, name='create_accommodation_order'),
    path('api/verify-customer/', views.verify_customer, name='verify_customer'),
    path('api/process-checkout/', views.process_checkout, name='process_checkout'),
    path('api/ac-status/', views.get_ac_status, name='get_ac_status'),
]
