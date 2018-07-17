from django.contrib import admin
from .models import Submission


class SubmissionAdmin(admin.ModelAdmin):
	list_display = ('id','myuser','problem','result','create_time')

admin.site.register(Submission,SubmissionAdmin)