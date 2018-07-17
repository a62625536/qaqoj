from django.contrib import admin
from django.urls import path,include
from .views import editDiscussion

urlpatterns = [
    path('<int:dis_id>',editDiscussion),
]

