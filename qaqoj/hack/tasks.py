from celery import task
from submission.models import Submission
from .models import Hack
from qaqoj.settings import BASE_DIR
import os
import lorun
import subprocess
import shutil

	
@task
def hack_submission(hack_id):
	hack = Hack.objects.get(pk=hack_id)
	submission = hack.submission
	hacker = hack.myuser
	owner = hack.submission.myuser
	hack.result = "评测中"
	hack.save()
	if submission.result != "答案正确":
		hack.result = "系统错误"
		hack.save()
		return True
	nowpath = os.path.join(BASE_DIR,'problem','problems',str(submission.problem.id))
	if not os.path.exists(nowpath):
		os.makedirs(nowpath)
	if not os.path.exists(nowpath+'/stand.cpp') or not os.path.exists(nowpath+'/check.cpp'):
		hack.result = "系统错误"
		hack.save()
	result = subprocess.getstatusoutput('g++ '+nowpath+'/check.cpp'+' -o temp -lm -O2 -DONLINE_JUDGE')
	if result[0] != 0:
		hack.result = "系统错误"
		hack.save()
		return True
	f = open('temp.in','w')
	f.write(str(hack.input_data))
	f.close()
	fin = open('temp.in')
	ftemp = open('temp.out','w')
	runcfg = {
		'args':['./temp'],
		'fd_in':fin.fileno(),
		'fd_out':ftemp.fileno(),
		'timelimit':5000, 
		'memorylimit':512*1024,
	}
	rst = lorun.run(runcfg)
	fin.close()
	ftemp.close()
	f = open('temp.out','r')
	if rst['result'] != 0:
		hack.result = "系统错误"
		hack.save()
		return True
	if f.readline().split()[0] != "YES":
		hack.result = "数据有误"
		hack.save()
		return True
	result = subprocess.getstatusoutput('g++ '+nowpath+'/stand.cpp'+' -o temp -lm -O2 -DONLINE_JUDGE')
	if result[0] != 0:
		hack.result = "系统错误"
		hack.save()
		return True
	fin = open('temp.in')
	ftemp = open('temp.out','w')
	runcfg = {
		'args':['./temp'],
		'fd_in':fin.fileno(),
		'fd_out':ftemp.fileno(),
		'timelimit':submission.problem.time_limit*1000, 
		'memorylimit':submission.problem.memory_limit*1024,
	}
	rst = lorun.run(runcfg)
	fin.close()
	ftemp.close()
	if rst['result'] != 0:
		hack.result = "系统错误"
		hack.save()
		return True


	if submission.language == 'C':
		f = open('temp.c','w')
	elif submission.language == 'C++':
		f = open('temp.cpp','w')
	elif submission.language == 'Java':
		f = open('Main.java','w')
	elif submission.language == 'Python3':
		f = open('temp.py','w')
	f.write(str(submission.code))
	f.close()

	if submission.language == 'C':
		result = subprocess.getstatusoutput('gcc temp.c -o temp -lm -O2 -DONLINE_JUDGE')
		argv = ['./temp']
	elif submission.language == 'C++':
		result = subprocess.getstatusoutput('g++ temp.cpp -o temp -lm -O2 -DONLINE_JUDGE')
		argv = ['./temp']
	elif submission.language == 'Java':
		result = subprocess.getstatusoutput('javac Main.java')
		argv = ['java','Main']
	elif submission.language == 'Python3':
		result = subprocess.getstatusoutput('python3 -m py_compile temp.py')
		argv = ['python3','__pycache__/temp.cpython-35.pyc']

	fin = open('temp.in')
	ftemp = open('temp2.out','w')
	runcfg = {
		'args':argv,
		'fd_in':fin.fileno(),
		'fd_out':ftemp.fileno(),
		'timelimit':submission.problem.time_limit*1000, 
		'memorylimit':submission.problem.memory_limit*1024,
	}
	rst = lorun.run(runcfg)
	fin.close()
	ftemp.close()
	ftemp1 = open('temp.out')
	ftemp2 = open('temp2.out')
	crst = lorun.check(ftemp1.fileno(),ftemp2.fileno())
	ftemp1.close()
	ftemp2.close()
	os.remove('temp2.out')
	if rst['result'] == 0 and crst == 0:
		hack.result = "失败"
		hack.save()
		return True
	hack.result = "成功"
	hack.save()
	hacker.hack_num += 1
	hacker.save()
	submission.problem.ac_num -= 1
	submission.problem.save()
	submission.result = "被Hack"
	submission.save()
	for i in range(1,10000):
		if not os.path.exists(nowpath+'/'+str(i)+'.in'):
			os.rename('temp.in',str(i)+'.in')
			os.rename('temp.out',str(i)+'.out')
			shutil.move(str(i)+'.in',nowpath)
			shutil.move(str(i)+'.out',nowpath)
			break
	submissions = Submission.objects.filter(myuser=owner,problem=submission.problem,result="答案正确")
	if len(submissions) == 0:
		owner.ac_num -= 1
		owner.ac_problems.remove(submission.problem)
		owner.save()
	return True
