from django.db import models
from account.models import MyUser
from submission.models import Submission

class Hack(models.Model):
	myuser = models.ForeignKey(MyUser,on_delete=models.CASCADE)
	submission = models.ForeignKey(Submission,on_delete=models.CASCADE)
	input_data = models.TextField()
	create_time = models.DateTimeField(auto_now_add=True)
	result = models.TextField(default="等待评测")

	def __str___(self):
		return 'user:'+self.user.username+' runID:'+str(self.submission.id)
	class Meta:
		ordering = ("-create_time",)