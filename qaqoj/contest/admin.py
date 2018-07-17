from django.contrib import admin
from .models import Contest,ContestUser,ContestSubmission

class ContestUserAdmin(admin.ModelAdmin):
	list_display = ('user','ac_num','sub_num')
admin.site.register(ContestUser,ContestUserAdmin)

class ContestSubmissionAdmin(admin.ModelAdmin):
	list_display = ('id','contestuser','problem','result','create_time')
admin.site.register(ContestSubmission,ContestSubmissionAdmin)

class ContestAdmin(admin.ModelAdmin):
	list_display = ('id','title','create_user','start_time','end_time')
admin.site.register(Contest,ContestAdmin)

