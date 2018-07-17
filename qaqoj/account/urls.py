from django.contrib import admin
from django.urls import path,include
from .views import getUserHome

urlpatterns = [
    path('<int:user_id>',getUserHome),
]
