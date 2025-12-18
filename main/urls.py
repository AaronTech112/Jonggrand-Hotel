from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("rooms/", views.rooms, name="rooms"),
    path("events/", views.events, name="events"),
    path("gallery/", views.gallery, name="gallery"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("room/<slug:slug>/", views.room_detail, name="room_detail"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("payment/verify/", views.payment_verify, name="payment_verify"),
    path("payment/<str:reference>/", views.payment_init, name="payment_init"),
    path("payment/success/<str:reference>/", views.payment_success, name="payment_success"),
]
