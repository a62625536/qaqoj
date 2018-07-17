from django.db import models

#定义类型：Announcement
class Announcement(models.Model):
    title = models.TextField()
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    visible = models.BooleanField(default=True)
    
    def __str__(self):
    	return self.title
    class Meta:
        ordering = ("-create_time",)
