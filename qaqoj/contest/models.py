from django.db import models
from problem.views import Problem
from django.contrib.auth.models import User

class ContestUser(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	ac_num = models.IntegerField(default=0)
	sub_num = models.IntegerField(default=0)
	ac_problems = models.ManyToManyField(Problem)

	def __str__(self):
		return self.user.username

class ContestSubmission(models.Model):
	contestuser = models.ForeignKey(ContestUser,on_delete=models.CASCADE)
	problem = models.ForeignKey(Problem,on_delete=models.CASCADE)
	language = models.TextField(default="C++")
	code = models.TextField()
	create_time = models.DateTimeField(auto_now_add=True)
	result = models.TextField(default="等待评测")
	memory = models.IntegerField(default=0)
	time = models.IntegerField(default=0)
	info = models.TextField()
	
	def __str___(self):
		return 'user:'+self.myuser.user.username+' to problem:'+self.problem.title
	class Meta:
		ordering = ("-create_time",)

class Contest(models.Model):
	title = models.TextField()
	create_user = models.ForeignKey(User,on_delete=models.CASCADE)
	description = models.TextField()
	problems = models.ManyToManyField(Problem)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	visible = models.BooleanField(default=False)
	create_time = models.DateTimeField(auto_now_add=True)
	contestusers = models.ManyToManyField(ContestUser)
	contestsubmissions = models.ManyToManyField(ContestSubmission)

	def __str__(self):
		return str(self.id)+':'+self.title
	class Meta:
		ordering = ("-create_time",)
