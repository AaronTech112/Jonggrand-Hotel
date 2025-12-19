from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("rooms/", views.rooms, name="rooms"),
    path("events/", views.events, name="events"),
    path("events/request/submit/", views.event_request_submit, name="event_request_submit"),
    path("events/request/success/<int:pk>/", views.event_request_success, name="event_request_success"),
    path("gallery/", views.gallery, name="gallery"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("contact/submit/", views.contact_submit, name="contact_submit"),
    path("contact/success/<int:pk>/", views.contact_request_success, name="contact_request_success"),
    path("room/<slug:slug>/", views.room_detail, name="room_detail"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("payment/verify/", views.payment_verify, name="payment_verify"),
    path("payment/<str:reference>/", views.payment_init, name="payment_init"),
    path("payment/success/<str:reference>/", views.payment_success, name="payment_success"),
]
