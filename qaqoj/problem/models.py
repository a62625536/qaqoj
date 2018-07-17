from django.db import models

#定义类型：Problem
class Problem(models.Model):
	title = models.TextField()
	time_limit = models.IntegerField(default=1)
	memory_limit = models.IntegerField(default=256)
	description = models.TextField()
	input_description = models.TextField()
	output_description = models.TextField()
	sample_input = models.TextField()
	sample_output = models.TextField()
	hint = models.TextField()
	ac_num = models.IntegerField(default=0)
	sub_num = models.IntegerField(default=0)
	visible = models.BooleanField(default=False)
	create_time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.id)+':'+self.title
	class Meta:
		ordering = ("create_time",)