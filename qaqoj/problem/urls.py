from django.contrib import admin
from django.urls import path,include
from .views import showProblem,showCheck,showStand,showCase

urlpatterns = [
	path('<int:problem_id>',showProblem),  
	path('<int:problem_id>/check',showCheck),
	path('<int:problem_id>/stand',showStand),
	path('<int:problem_id>/case/<int:case_id>',showCase),
]
