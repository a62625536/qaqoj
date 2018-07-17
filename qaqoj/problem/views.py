from django.shortcuts import render,redirect 
from account.models import MyUser
from submission.models import Submission
from django.core.paginator import Paginator
from .models import Problem
from qaqoj.settings import BASE_DIR
from submission.tasks import test_submission
import os

#业务逻辑：显示问题列表
def showProblemsList(request):
	problems_all = Problem.objects.all()
	paginator = Paginator(problems_all,15)
	page_num = request.GET.get('page',1)
	problems = paginator.get_page(page_num)
	page_num = problems.number
	page_range = range(max(1,page_num-2),min(page_num+3,paginator.num_pages+1))
	try:#判断用户是否已登录
		myuser = MyUser.objects.get(user_id = request.user.id)
		return render(request,'problem_list.html',{'problems':problems,'page_range':page_range,'myuser':myuser})
	except:
		return render(request,'problem_list.html',{'problems':problems,'page_range':page_range})
	
#业务逻辑：显示问题
def showProblem(request,problem_id):
	try:#判断目标问题是否存在
		problem = Problem.objects.get(pk=problem_id)
	except:
		return redirect('/problems')
	if request.user.is_staff or problem.visible:#用户是管理员或目标问题可显示
		return render(request,'problem.html',{'problem':problem})
	else:#用户不是管理员且目标问题不可显示
		return redirect('/problems')

#业务逻辑：添加问题
def addProblem(request):
	if not request.user.is_staff:#用户不是管理员
		return redirect('/problems')
	else:#用户是管理员
		if request.method == "POST":#POST请求
			problem = Problem()
			problem.title = request.POST.get('title')
			problem.time_limit = request.POST.get('time_limit')
			problem.memory_limit = request.POST.get('memory_limit')
			problem.description = request.POST.get('description')
			problem.input_description = request.POST.get('input_description')
			problem.output_description = request.POST.get('output_description')
			problem.sample_input = request.POST.get('sample_input')
			problem.sample_output = request.POST.get('sample_output')
			problem.hint = request.POST.get('hint')
			problem.save()
			return redirect('/problem/'+str(problem.id))
		else:#GET请求
			return render(request,"problem_add.html")
			
#业务逻辑：更新问题
def updateProblem(request):
	problem_id = request.GET.get('problem_id')
	try:#判断问题是否存在
		problem = Problem.objects.get(id=problem_id)
	except:
		return redirect('/problems')
	if not request.user.is_staff:#用户不是管理员
		return redirect('/problems')
	else:#用户是管理员
		nowpath = os.path.join(BASE_DIR,'problem','problems',problem_id)
		if not os.path.exists(nowpath):
			os.makedirs(nowpath)
		if os.path.exists(nowpath+'/stand.cpp'):
			has_standcode = True
		else:
			has_standcode = False
		if os.path.exists(nowpath+'/check.cpp'):
			has_checkcode = True
		else:
			has_checkcode = False
		case = []
		for file in os.listdir(nowpath):
			if os.path.splitext(file)[1] == '.in':
				case.append(os.path.splitext(file)[0])
		case = sorted(case)
		if request.method != "POST":#GET请求
			return render(request,'problem_update.html',{'problem':problem,'standcode':has_standcode,'checkcode':has_checkcode,'cases':case})
		else:#POST请求
			if len(request.POST) == 0 and len(request.FILES) == 0:#更新问题为不可见
				if problem.visible == True:
					problem.visible = False
					problem.save()
					for myuser in MyUser.objects.all():
						if problem in myuser.ac_problems.all():
							myuser.ac_num -= 1
							myuser.save()
				return redirect('/updateproblem?problem_id='+str(problem.id))
			elif len(request.POST) == 1:#更新问题为可见
				if problem.visible == False:
					problem.visible = True
					problem.save()
					for myuser in MyUser.objects.all():
						if problem in myuser.ac_problems.all():
							myuser.ac_num += 1
							myuser.save()
				return redirect('/updateproblem?problem_id='+str(problem.id))
			elif len(request.FILES) == 1 and request.FILES.get('checkcode',0):#上传检查程序
				obj = request.FILES.get('checkcode')
				f = open(nowpath+'/check.cpp','wb')
				for chunk in obj.chunks():
					f.write(chunk)
				f.close()
				return redirect('/updateproblem?problem_id='+str(problem.id))
			elif len(request.FILES) == 1:#上传标准程序
				obj = request.FILES.get('standcode')
				f = open(nowpath+'/stand.cpp','wb')
				for chunk in obj.chunks():
					f.write(chunk)
				f.close()
				return redirect('/updateproblem?problem_id='+str(problem.id))
			elif len(request.FILES) == 2:#上传测试数据
				inputfile = request.FILES.get('input')
				outputfile = request.FILES.get('output')
				for i in range(1,10000):
					if not os.path.exists(nowpath+'/'+str(i)+'.in'):
						f = open(nowpath+'/'+str(i)+'.in','wb')
						for chunk in inputfile.chunks():
							f.write(chunk)
						f.close()
						f = open(nowpath+'/'+str(i)+'.out','wb')
						for chunk in outputfile.chunks():
							f.write(chunk)
						f.close()
						case.append(str(i))
						break
				case = sorted(case)
				return redirect('/updateproblem?problem_id='+str(problem.id))
			else:#更新问题内容
				problem.title = request.POST.get('title')
				problem.time_limit = request.POST.get('time_limit')
				problem.memory_limit = request.POST.get('memory_limit')
				problem.description = request.POST.get('description')
				problem.input_description = request.POST.get('input_description')
				problem.output_description = request.POST.get('output_description')
				problem.sample_input = request.POST.get('sample_input')
				problem.sample_output = request.POST.get('sample_output')
				problem.hint = request.POST.get('hint')
				problem.save()
				return redirect('/problem/'+problem_id)

#业务逻辑：显示测试程序
def showCheck(request,problem_id):
	try:#判断目标问题是否存在
		problem = Problem.objects.get(id=problem_id)
	except:
		return redirect('/problems')
	if not request.user.is_staff:#用户不是管理员
		return redirect('/problems')
	else:#用户是管理员
		nowpath = os.path.join(BASE_DIR,'problem','problems',str(problem_id),'check.cpp')
		if os.path.exists(nowpath):#测试程序存在
			f = open(nowpath,'r')
			text = ''
			for line in f.readlines():
				text += line
			f.close()
			return render(request,'problem_check.html',{'problem':problem,'text':text})
		else:#测试程序不存在
			return redirect('/updateproblem?problem_id='+str(problem_id))

#业务逻辑：显示标准程序
def showStand(request,problem_id):
	try:#判断目标问题是否存在
		problem = Problem.objects.get(id=problem_id)
	except:
		return redirect('/problems')
	if not request.user.is_staff:#用户不是管理员
		return redirect('/problems')
	else:#用户是管理员
		nowpath = os.path.join(BASE_DIR,'problem','problems',str(problem_id),'stand.cpp')
		if os.path.exists(nowpath):#标准程序存在
			f = open(nowpath,'r')
			text = ''
			for line in f.readlines():
				text += line
			f.close()
			return render(request,'problem_stand.html',{'problem':problem,'text':text})
		else:#标准程序不存在
			return redirect('/updateproblem?problem_id='+str(problem_id))

#业务逻辑：显示测试数据
def showCase(request,problem_id,case_id):
	try:#判断目标问题是否存在
		problem = Problem.objects.get(id=problem_id)
	except:
		return redirect('/problems')
	if not request.user.is_staff:#用户不是管理员
		return redirect('/problems')
	else:#用户是管理员
		nowpath = os.path.join(BASE_DIR,'problem','problems',str(problem_id),str(case_id))
		if os.path.exists(nowpath+'.in'):#测试数据存在
			if request.method == "POST":#POST请求
				os.remove(nowpath+'.in')
				os.remove(nowpath+'.out')
				return redirect('/updateproblem?problem_id='+str(problem_id))
			else:#GET请求
				f = open(nowpath+'.in','r')
				input_text = ''
				for line in f.readlines():
					input_text += line
				f.close()
				f = open(nowpath+'.out','r')
				output_text = ''
				for line in f.readlines():
					output_text += line
				f.close()
				return render(request,'problem_case.html',{'problem':problem,'case_id':case_id,'input_text':input_text,'output_text':output_text})
		else:#测试数据不存在
			return redirect('/updateproblem?problem_id='+str(problem_id))

#业务逻辑：提交测试代码
def submitProblem(request):
	problem_id = request.GET.get('problem_id')
	try:#判断目标问题是否存在
		problem = Problem.objects.get(id=problem_id)
	except:
		return redirect('/problems')
	if not request.user.is_authenticated:#用户未登录
		return redirect('/login')
	else:#用户已登录
		if not problem.visible and not request.user.is_staff:#问题不可见且用户不是管理员
			return redirect('/problems')
		else:#问题可见或用户是管理员
			if request.method == "POST":#POST请求
				submission = Submission()
				submission.myuser = MyUser.objects.get(user_id = request.user.id)
				submission.problem = problem
				submission.language = request.POST.get('language')
				submission.code = request.POST.get('code')
				submission.myuser.sub_num += 1
				problem.sub_num += 1
				submission.myuser.save()
				problem.save()
				submission.save()
				test_submission.delay(submission.id)
				return redirect('/status')
			else:#GET请求
				return render(request,'problem_submit.html')
		
#业务逻辑：获取排名
def showRank(request):
	rank_type = request.GET.get('rank_type','1')
	if rank_type == '1':
		users_all = MyUser.objects.all().order_by('-ac_num','sub_num','id')
	else:
		users_all = MyUser.objects.all().order_by('-hack_num','sub_num','id')
	paginator = Paginator(users_all,20)
	page_num = request.GET.get('page',1)
	users = paginator.get_page(page_num)
	page_num = users.number
	page_range = range(max(1,page_num-2),min(page_num+3,paginator.num_pages+1))
	return render(request,'rank.html',{'users':users,'page_range':page_range})