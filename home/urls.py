from django.urls import path
from home import views

urlpatterns = [
    path('', views.home_home, name='home_home'),
    path('hotel-details/<id>', views.home_hotel_single, name='home_hotel_single'),
    path('hotel-details/<id>/search', views.home_hotel_single_search, name='home_hotel_single_search'),
    path('hotel-booking', views.home_hotel_booking, name='home_hotel_booking'),
    # 
    path('order-success', views.home_success, name='home_success'),
    path('order-cancel', views.home_cancel, name='home_cancel'),
    path('hotel-booking-stripe', views.home_hotel_booking_stripe, name='home_hotel_booking_stripe'),

]