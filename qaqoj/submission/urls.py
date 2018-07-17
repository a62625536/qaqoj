from django.contrib import admin
from django.urls import path
from .views import showSubmission

urlpatterns = [
    path('<int:submission_id>',showSubmission),
]

