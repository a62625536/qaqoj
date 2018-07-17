from django.contrib import admin
from .models import Discussion


class DiscussionAdmin(admin.ModelAdmin):
	list_display = ('id','user','content','visible','create_time',)

admin.site.register(Discussion,DiscussionAdmin)