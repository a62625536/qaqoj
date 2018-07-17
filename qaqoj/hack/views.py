from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from submission.models import Submission
from account.models import MyUser
from .models import Hack
from .tasks import hack_submission

#业务逻辑：提交Hack
def submitHack(request):
	submission_id = request.GET.get('submission_id')
	try:#判断目标提交记录是否存在
		submission = Submission.objects.get(pk=submission_id)
	except:
		return redirect('/status')
	try:#判断用户是否登录
		myuser = MyUser.objects.get(user_id=request.user.id)
	except:
		return redirect('/status')
	if submission.myuser == myuser or submission.problem not in myuser.ac_problems.all() or submission.result != "答案正确":#用户自身的提交或用户未过该问题或目标提交记录结果不正确
		return redirect('/submission/'+str(submission.id))
	else:#非用户自身的提交且用户已过该问题且目标提交记录结果正确
		if request.method == "POST":#POST请求
			hack = Hack()
			hack.myuser = myuser
			hack.submission = submission
			hack.input_data = request.POST.get('input_data')
			hack.save()
			hack_submission.delay(hack.id)
			return redirect('/hacks')
		else:#GET请求
			return render(request,'hack_submit.html')

#业务逻辑：显示Hack记录列表
def showHackList(request):
	hack_type = request.GET.get('hack_type','1')
	if request.user.is_authenticated and hack_type == '2':
		myuser = MyUser.objects.get(user_id=request.user.id)
		hacks_all = Hack.objects.filter(myuser=myuser)
	else:
		hacks_all = Hack.objects.all()
	paginator = Paginator(hacks_all,20)
	page_num = request.GET.get('page',1)
	hacks = paginator.get_page(page_num)
	page_num = hacks.number
	page_range = range(max(1,page_num-2),min(page_num+3,paginator.num_pages+1))
	try:#判断用户是否登录
		myuser = MyUser.objects.get(pk = request.user.id)
		return render(request,'hack_list.html',{'hacks':hacks,'page_range':page_range,'myuser':myuser})
	except:
		return render(request,'hack_list.html',{'hacks':hacks,'page_range':page_range})

#业务逻辑：显示Hack记录
def showHack(request,hack_id):
	try:#判断Hack记录是否存在
		hack = Hack.objects.get(pk=hack_id)
	except:
		return redirect('/hacks')
	try:
		myuser = MyUser.objects.get(pk=request.user.id)
	except:#判断用户是否登录
		return redirect('/hacks')
	if request.user.is_staff or hack.myuser == myuser:#用户自身的Hack记录
		return render(request,'hack.html',{'hack':hack,'myuser':myuser})
	else:#非用户自身的Hack记录
		return redirect('/hacks')
