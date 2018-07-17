from django.contrib import admin
from .models import Hack

class HackAdmin(admin.ModelAdmin):
	list_display = ('myuser','submission','result','result','create_time')

admin.site.register(Hack,HackAdmin)
