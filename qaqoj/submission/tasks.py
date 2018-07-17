from celery import task
from submission.models import Submission
from qaqoj.settings import BASE_DIR
import os
import lorun
import subprocess
import time

RESULT_STR = [
	'答案正确',
	'格式错误',
	'时间超限',
	'内存超限',
	'答案错误',
	'运行错误',
	'输出超限',
	'编译错误',
	'系统错误',
]


@task
def test_submission(submission_id):
	submission = Submission.objects.get(pk=submission_id)
	if submission.language == 'C':
		f = open('temp.c','w')
	elif submission.language == 'C++':
		f = open('temp.cpp','w')
	elif submission.language == 'Java':
		f = open('Main.java','w')
	elif submission.language == 'Python3':
		f = open('temp.py','w')
	else:
		submission.result = '系统错误'
		submission.save()
		return True
	f.write(str(submission.code))
	f.close()

	if submission.language == 'C':
		result = subprocess.getstatusoutput('gcc temp.c -o temp -lm -O2 -DONLINE_JUDGE')
		if result[0] != 0:
			submission.result = '编译错误'
			submission.info = result[1]
			submission.save()
			return True
		argv = ['./temp']
	elif submission.language == 'C++':
		result = subprocess.getstatusoutput('g++ temp.cpp -o temp -lm -O2 -DONLINE_JUDGE')
		if result[0] != 0:
			submission.result = '编译错误'
			submission.info = result[1]
			submission.save()
			return True
		argv = ['./temp']
	elif submission.language == 'Java':
		result = subprocess.getstatusoutput('javac Main.java')
		if result[0] != 0:
			submission.result = '编译错误'
			submission.info = result[1]
			submission.save()
			return True
		argv = ['java','Main']
	elif submission.language == 'Python3':
		result = subprocess.getstatusoutput('python3 -m py_compile temp.py')
		if result[0] != 0:
			submission.result = '编译错误'
			submission.info = result[1]
			submission.save()
			return True
		argv = ['python3','__pycache__/temp.cpython-35.pyc']
	nowpath = os.path.join(BASE_DIR,'problem','problems',str(submission.problem.id))
	if not os.path.exists(nowpath):
		os.makedirs(nowpath)
	submission.result = '评测中'
	submission.save()
	maxtime = 0
	maxmemory = 0
	ok = 1
	for file in os.listdir(nowpath):
		if os.path.splitext(file)[1] == '.in':
			file_in = os.path.join(nowpath,os.path.splitext(file)[0]+'.in')
			file_out = os.path.join(nowpath,os.path.splitext(file)[0]+'.out')
			fin = open(file_in)
			ftemp = open('temp.out','w')
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
			maxtime = max(maxtime,rst['timeused'])
			maxmemory = max(maxmemory,rst['memoryused'])
			if rst['result'] == 0:
				ftemp = open('temp.out')
				fout = open(file_out)
				crst = lorun.check(fout.fileno(), ftemp.fileno())
				fout.close()
				ftemp.close()
				#os.remove('temp.out')
				rst['result'] = crst
			if rst['result'] != 0:
				ok = 0
				submission.result = RESULT_STR[rst['result']]
				break
	if ok:
		submission.result = "答案正确"
		submission.problem.ac_num += 1
		submission.problem.save()
		print(submission.myuser.ac_num)
		if submission.problem not in submission.myuser.ac_problems.all():
			submission.myuser.ac_problems.add(submission.problem)
			submission.myuser.ac_num += 1
			submission.myuser.save()

	submission.time = maxtime+15
	submission.memory = maxmemory
	submission.save()
	return True
