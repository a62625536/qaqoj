from django.contrib import admin
from .models import Problem


class ProblemAdmin(admin.ModelAdmin):
	list_display = ('id','title','ac_num','sub_num','create_time')

admin.site.register(Problem,ProblemAdmin)