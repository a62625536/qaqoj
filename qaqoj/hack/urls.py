from django.contrib import admin
from django.urls import path,include
from .views import showHack

urlpatterns = [
	path('<int:hack_id>',showHack),  
]
