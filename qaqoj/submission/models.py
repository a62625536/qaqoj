from django.db import models
from account.models import MyUser
from problem.models import Problem

class Submission(models.Model):
	myuser = models.ForeignKey(MyUser,on_delete=models.CASCADE)
	problem = models.ForeignKey(Problem,on_delete=models.CASCADE)
	language = models.TextField(default="C++")
	code = models.TextField()
	create_time = models.DateTimeField(auto_now_add=True)
	result = models.TextField(default="等待评测")
	memory = models.IntegerField(default=0)
	time = models.IntegerField(default=0)
	info = models.TextField(null=True)
	
	def __str___(self):
		return 'user:'+self.myuser.user.username+' to problem:'+self.problem.title
	class Meta:
		ordering = ("-create_time",)