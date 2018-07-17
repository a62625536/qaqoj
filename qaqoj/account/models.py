from django.db import models
from django.contrib.auth.models import User
from problem.models import Problem

#定义类型：MyUser
class MyUser(models.Model):
	user = models.OneToOneField(User,unique=True,on_delete=models.CASCADE)
	ac_problems = models.ManyToManyField(Problem)
	ac_num = models.IntegerField(default=0)
	sub_num = models.IntegerField(default=0)
	hack_num = models.IntegerField(default=0)
	
	def __str__(self):
		return self.user.username



