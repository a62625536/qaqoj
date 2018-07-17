from django.db import models
from django.contrib.auth.models import User

#定义类型：Discussion
class Discussion(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	content = models.TextField()
	visible = models.BooleanField(default=True)
	create_time = models.DateTimeField(auto_now_add=True)
    
	def __str__(self):
		return str(self.id)
	class Meta:
		db_table = "discussion"
		ordering = ("-create_time",)