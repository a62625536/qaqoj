from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from .models import Submission
from account.models import MyUser

#业务逻辑：显示提交记录列表
def showSubmissionList(request):
	status_type = request.GET.get('status_type','1')
	if request.user.is_authenticated and status_type == '2':
		myuser = MyUser.objects.get(user_id=request.user.id)
		submission_all = Submission.objects.filter(myuser=myuser)
	else:
		submission_all = Submission.objects.all()
	paginator = Paginator(submission_all,20)
	page_num = request.GET.get('page',1)
	submissions = paginator.get_page(page_num)
	page_num = submissions.number
	page_range = range(max(1,page_num-2),min(page_num+3,paginator.num_pages+1))
	try:#判断用户是否登录
		myuser = MyUser.objects.get(pk=request.user.id)
		return render(request,'status.html',{'submissions':submissions,'page_range':page_range,'myuser':myuser})
	except:
		return render(request,'status.html',{'submissions':submissions,'page_range':page_range})

#业务逻辑：显示提交记录
def showSubmission(request,submission_id):
	try:#判断目标提交记录不存在
		submission = Submission.objects.get(pk=submission_id)
	except:
		return redirect('/status')
	try:#判断用户是否登录
		myuser = MyUser.objects.get(user_id=request.user.id)
	except:
		return redirect('/status')
	if request.user.is_staff or submission.myuser == myuser or submission.problem in myuser.ac_problems.all() and submission.result == "答案正确":#用户自身的提交或用户已过的题的正确提交
		return render(request,'submission.html',{'submission':submission,'myuser':myuser})
	else:#非用户自身的提交且非用户已过的题的正确提交
		return redirect('/status')


	
