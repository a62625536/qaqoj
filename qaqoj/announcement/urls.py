from django.contrib import admin
from django.urls import path,include
from .views import showAnnouncement,updateAnnouncement

urlpatterns = [
    path('<int:announcement_id>',showAnnouncement),
    path('<int:announcement_id>/update',updateAnnouncement),
]
