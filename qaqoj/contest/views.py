from django.shortcuts import render,redirect 
from django.core.paginator import Paginator
from .models import ContestUser,ContestSubmission,Contest
from account.models import MyUser
from problem.models import Problem
from django.utils import timezone
from .tasks import test_contestsubmission

#业务逻辑：显示比赛列表
def showContestList(request):
	now = timezone.now()
	contests_all = Contest.objects.all()
	paginator = Paginator(contests_all,20)
	page_num = request.GET.get('page',1)
	contests = paginator.get_page(page_num)
	page_num = contests.number
	page_range = range(max(1,page_num-2),min(page_num+3,paginator.num_pages+1))
	contests_and_joineds = []
	if request.user.is_authenticated:#用户已登录
		for contest in contests.object_list:
			contest_and_joined = {}
			contest_and_joined['contest'] = contest
			joined = False
			for contestuser in contest.contestusers.all():
				if request.user == contestuser.user:
					joined = True
			contest_and_joined['joined'] = joined
			contests_and_joineds.append(contest_and_joined)
	else:#用户未登录
		for contest in contests.object_list:
			contest_and_joined = {}
			contest_and_joined['contest'] = contest
			contest_and_joined['joined'] = False
			contests_and_joineds.append(contest_and_joined)
	return render(request,'contest_list.html',{'contests':contests,'page_range':page_range,'now':now,'contests_and_joineds':contests_and_joineds})
	
#业务逻辑：添加比赛
def addContest(request):
	if not request.user.is_staff:#用户不是管理员
		return redirect('/contests')
	else:#用户是管理员
		problems = Problem.objects.all()
		if request.method == "POST":#POST选项
			now = str(timezone.now()).split()
			now = now[0]+'T'+now[1]
			if request.POST.get('start_time') < now:#开始时间小于当前时间			
				return render(request,'contest_add.html',{'problems':problems,'info':"你穿越了？"})
			if request.POST.get('start_time') > request.POST.get('end_time'):#开始时间大于结束时间
				return render(request,'contest_add.html',{'problems':problems,'info':"时间扭曲？"})
			else:#比赛数据正常
				contest = Contest()
				contest.create_user = request.user
				contest.title = request.POST.get('title')
				contest.description = request.POST.get('description')
				contest.start_time = request.POST.get('start_time')
				contest.end_time = request.POST.get('end_time')
				problem_ids = request.POST.getlist('problem')
				contest.save()
				for problem_id in problem_ids:
					contest.problems.add(Problem.objects.get(pk=problem_id))
				return redirect('/contests')
		else:#GET选项
			return render(request,'contest_add.html',{'problems':problems})

#业务逻辑：显示比赛主页
def showContest(request,contest_id):
	try:#判断目标比赛是否存在
		contest = Contest.objects.get(pk=contest_id)
	except:
		return redirect('/contests')
	if not request.user.is_authenticated:#判断用户是否登录
		return redirect('/login')
	else:
		if contest.visible or request.user == contest.create_user or request.user.is_superuser:#比赛可见或用户是创建者或用户是超级管理员
			if contest.end_time < timezone.now():#比赛已结束
				return render(request,'contest_home.html',{'contest':contest,'ok':True})
			else:#比赛未结束
				joined = False
				for contestuser in contest.contestusers.all():
					if request.user == contestuser.user:
						joined = True
						break
				if joined:#用户已报名
					return render(request,'contest_home.html',{'contest':contest,'ok':True})
				else:#用户已报名
					if request.method == "POST":#POST请求
						contestuser = ContestUser()
						contestuser.user = request.user
						contestuser.save()
						contest.contestusers.add(contestuser)
						contest.save()
						return render(request,'contest_home.html',{'contest':contest,'ok':True})
					else:#GET请求
						return render(request,'contest_home.html',{'contest':contest,'ok':False})
		else:#无权限且问题不可显示
			return redirect('/contests')

#业务逻辑：更新比赛
def updateContest(request,contest_id):
	try:#判断目标比赛是否存在
		contest = Contest.objects.get(pk=contest_id)
	except:
		return redirect('/contests')
	if not request.user.is_superuser and not request.user == contest.create_user:#用户不是创建者且用户不是超级管理员
		return redirect('/contest/'+str(contest_id))
	else:#用户有管理权限
		problems = Problem.objects.all()
		if request.method == "POST":#POST请求
			if len(request.POST) == 0:#隐藏比赛
				contest.visible = False
				contest.save()
				return redirect('/contest/'+str(contest.id)+'/update')
			elif len(request.POST) == 1:#显示比赛
				contest.visible = True
				contest.save()
				return redirect('/contest/'+str(contest.id)+'/update')
			else:#更新内容
				now = str(timezone.now()).split()
				now = now[0]+'T'+now[1]
				if request.POST.get('start_time') > request.POST.get('end_time'):#开始时间大于结束时间
					return render(request,'contest_update.html',{'problems':problems,'contest':contest,'info':"时间扭曲？"})
				else:#比赛数据正常
					contest.create_user = request.user
					contest.title = request.POST.get('title')
					contest.description = request.POST.get('description')
					contest.start_time = request.POST.get('start_time')
					contest.end_time = request.POST.get('end_time')
					problem_ids = request.POST.getlist('problem')
					new_problems = []
					for problem_id in problem_ids:
						new_problems.append(Problem.objects.get(pk=problem_id))
					for old_problem in contest.problems.all():
						if old_problem not in new_problems:
							for contestuser in contest.contestusers.all():
								if old_problem in contestuser.ac_problems.all():
									contestuser.ac_num -= 1
									contestuser.save()
							contest.problems.remove(old_problem)
					for new_problem in new_problems:
						if new_problem not in contest.problems.all():
							contest.problems.add(new_problem)
							for contestuser in contest.contestusers.all():
								if new_problem in contestuser.ac_problems.all():
									contestuser.ac_num += 1
									contestuser.save()
					contest.save()
					return redirect('/contest/'+str(contest_id))
		else:#GET请求
			return render(request,'contest_update.html',{'problems':problems,'contest':contest})

#业务逻辑：显示比赛题目列表
def showContestProblemList(request,contest_id):
	try:#判断目标比赛是否存在
		contest = Contest.objects.get(pk=contest_id)
	except:
		return redirect('/contests')
	if contest.start_time > timezone.now():#比赛未开始
		return render(request,'contest_problemlist.html',{'contest':contest,'info':"未开始"})
	else:#比赛已开始
		joined = False
		for contestuser in contest.contestusers.all():
			if request.user == contestuser.user:
				now_contestuser = contestuser
				joined = True
				break
		if timezone.now() < contest.end_time and not joined:#比赛进行中用户未报名
			return render(request,'contest_problemlist.html',{'contest':contest,'info':"未报名"})
		else:#比赛已结束或用户已报名
			problems = contest.problems.all()
			contestsubmissions = contest.contestsubmissions.all()
			problems_and_nums = []
			for problem in problems:
				problem_and_num = {}
				problem_and_num['problem'] = problem
				ac_num = 0
				sub_num = 0
				for contestsubmission in contestsubmissions:
					if contestsubmission.problem == problem:
						sub_num += 1
						if contestsubmission.result == "答案正确":
							ac_num += 1
				problem_and_num['ac_num'] = ac_num
				problem_and_num['sub_num'] = sub_num
				problems_and_nums.append(problem_and_num)
			if joined:
			    return render(request,'contest_problemlist.html',{'contest':contest,'contestuser':now_contestuser,'problems_and_nums':problems_and_nums,'running':timezone.now() < contest.end_time})
			else:
			    return render(request,'contest_problemlist.html',{'contest':contest,'problems_and_nums':problems_and_nums,'running':timezone.now() < contest.end_time})

#业务逻辑：显示比赛问题
def showContestProblem(request,contest_id,problem_id):
	try:#判断目标比赛是否存在
		contest = Contest.objects.get(pk=contest_id)
	except:
		return redirect('/contests')
	try:#判断目标问题是否存在
		problem = Problem.objects.get(pk=problem_id)
	except:
		return redirect('/contest/'+str(contest_id))
	if problem not in contest.problems.all():#问题不在比赛问题列表中
		return redirect('/contest/'+str(contest_id))
	else:#问题在比赛问题列表中
		joined = False
		for contestuser in contest.contestusers.all():
			if request.user == contestuser.user:
				joined = True
				break
		if contest.start_time > timezone.now() or timezone.now() > contest.end_time or not joined:#比赛未开始或比赛已结束或用户未注册
			return redirect('/contest/'+str(contest_id))
		else:#比赛进行中且用户已注册
			ac_num = 0
			sub_num = 0
			for contestsubmission in contest.contestsubmissions.all():
				if problem == contestsubmission.problem:
					sub_num += 1
					if contestsubmission.result == "Accepted":
						ac_num += 1
			return render(request,'contest_problem.html',{'contest':contest,'problem':problem,'ac_num':ac_num,'sub_num':sub_num})

#业务逻辑：提交比赛问题测试代码
def submitContestProblem(request,contest_id):
	problem_id = request.GET.get('problem_id')
	try:#判断目标比赛是否存在
		contest = Contest.objects.get(pk=contest_id)
	except:
		return redirect('/contests')
	try:#判断目标问题是否存在
		problem = Problem.objects.get(pk=problem_id)
	except:
		return redirect('/contest/'+str(contest_id))
	if problem not in contest.problems.all():#问题不在比赛问题列表中
		return redirect('/contest/'+str(contest_id))
	else:#问题在比赛问题列表中
		joined = False
		for contestuser in contest.contestusers.all():
			if request.user == contestuser.user:
				submit_contestuser = contestuser
				joined = True
				break
		if contest.start_time > timezone.now() or timezone.now() > contest.end_time or not joined:#比赛未开始或比赛已结束或用户未注册
			return redirect('/contest/'+str(contest_id))
		else:#比赛进行中且用户已注册
			if request.method == "POST":#POST选项
				contestsubmission = ContestSubmission()
				contestsubmission.contestuser = submit_contestuser
				contestsubmission.problem = problem
				contestsubmission.language = request.POST.get('language')
				contestsubmission.code = request.POST.get('code')
				contestsubmission.save()
				contestsubmission.contestuser.sub_num += 1
				contestsubmission.contestuser.save()
				contest.contestsubmissions.add(contestsubmission)
				contest.save()
				test_contestsubmission.delay(contestsubmission.id)
				return redirect('/contest/'+str(contest.id)+'/status')
			else:#GET选项
				return render(request,'contest_submit.html',{'contest':contest})

#业务逻辑：显示比赛提交记录列表
def showContestStatus(request,contest_id):
	try:#判断目标比赛是否存在
		contest = Contest.objects.get(pk=contest_id)
	except:
		return redirect('/contests')
	if not request.user.is_authenticated:#用户未登录
		return redirect('/login')
	else:#用户已登录
		contest = Contest.objects.get(pk=contest_id)
		contestsubmissions_all = contest.contestsubmissions.all()
		paginator = Paginator(contestsubmissions_all,15)
		page_num = request.GET.get('page',1)
		contestsubmissions = paginator.get_page(page_num)
		page_num = contestsubmissions.number
		page_range = range(max(1,page_num-2),min(page_num+3,paginator.num_pages+1))
		try:#判断用户是否已报名
			contestuser = contest.contestusers.get(user=request.user)
			return render(request,'contest_status.html',{'contest':contest,'page_range':page_range,'contestsubmissions':contestsubmissions,'contestuser':contestuser})
		except:
			return render(request,'contest_status.html',{'contest':contest,'page_range':page_range,'contestsubmissions':contestsubmissions})

#业务逻辑：显示比赛提交记录
def showContestSubmission(request,contest_id,contestsubmission_id):
	try:#判断目标比赛是否存在
		contest = Contest.objects.get(pk=contest_id)
	except:
		return redirect('/contests')
	try:#提交记录是否存在与用户是否报名
		contestsubmission = ContestSubmission.objects.get(pk=contestsubmission_id)
		contestuser = contest.contestusers.get(user=request.user)
	except:
		return redirect('/contest/'+str(contest.id)+'/status')
	if request.user.is_superuser or contestuser.user == contest.create_user or contestsubmission.contestuser == contestuser:#用户有管理权限或为用户自身的提交记录
		return render(request,'contest_submission.html',{'contest':contest,'contestsubmission':contestsubmission})
	else:#用户无管理权限且非用户自身的提交记录
		return redirect('/contest/'+str(contest.id)+'/status')

#业务逻辑：显示比赛排名列表
def showContestRank(request,contest_id):
	try:#判断目标比赛是否存在
		contest = Contest.objects.get(pk=contest_id)
	except:
		return redirect('/contests')
	contestusers_all = contest.contestusers.all().order_by('-ac_num','sub_num','id')
	paginator = Paginator(contestusers_all,20)
	page_num = request.GET.get('page',1)
	contestusers = paginator.get_page(page_num)
	page_num = contestusers.number
	page_range = range(max(1,page_num-2),min(page_num+3,paginator.num_pages+1))
	return render(request,'contest_rank.html',{'contest':contest,'contestusers':contestusers,'page_range':page_range})
