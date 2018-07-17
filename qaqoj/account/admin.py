from django.contrib import admin
from .models import MyUser

class MyUserAdmin(admin.ModelAdmin):
	list_display = ('user','ac_num','sub_num')

admin.site.register(MyUser,MyUserAdmin)
