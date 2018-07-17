from celery import task
from .models import Contest,ContestSubmission,ContestUser
from qaqoj.settings import BASE_DIR
import os
import lorun
import subprocess

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
def test_contestsubmission(contestsubmission_id):
	contestsubmission = ContestSubmission.objects.get(pk=contestsubmission_id)
	if contestsubmission.language == 'C':
		f = open('temp.c','w')
	elif contestsubmission.language == 'C++':
		f = open('temp.cpp','w')
	elif contestsubmission.language == 'Java':
		f = open('Main.java','w')
	elif contestsubmission.language == 'Python3':
		f = open('temp.py','w')
	else:
		contestsubmission.result = '系统错误'
		contestsubmission.save()
		return True
	f.write(str(contestsubmission.code))
	f.close()

	if contestsubmission.language == 'C':
		result = subprocess.getstatusoutput('gcc temp.c -o temp -lm -O2 -DONLINE_JUDGE')
		if result[0] != 0:
			contestsubmission.result = '编译错误'
			contestsubmission.info = result[1]
			contestsubmission.save()
			return True
		argv = ['./temp']
	elif contestsubmission.language == 'C++':
		result = subprocess.getstatusoutput('g++ temp.cpp -o temp -lm -O2 -DONLINE_JUDGE')
		if result[0] != 0:
			contestsubmission.result = '编译错误'
			contestsubmission.info = result[1]
			contestsubmission.save()
			return True
		argv = ['./temp']
	elif contestsubmission.language == 'Java':
		result = subprocess.getstatusoutput('javac Main.java')
		if result[0] != 0:
			contestsubmission.result = '编译错误'
			contestsubmission.info = result[1]
			contestsubmission.save()
			return True
		argv = ['java','Main']
	elif contestsubmission.language == 'Python3':
		result = subprocess.getstatusoutput('python3 -m py_compile temp.py')
		if result[0] != 0:
			contestsubmission.result = '编译错误'
			contestsubmission.info = result[1]
			contestsubmission.save()
			return True
		argv = ['python3','__pycache__/temp.cpython-35.pyc']
	nowpath = os.path.join(BASE_DIR,'problem','problems',str(contestsubmission.problem.id))
	if not os.path.exists(nowpath):
		os.makedirs(nowpath)
	contestsubmission.result = '评测中'
	contestsubmission.save()
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
				'timelimit':contestsubmission.problem.time_limit*1000, 
				'memorylimit':contestsubmission.problem.memory_limit*1024,
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
				contestsubmission.result = RESULT_STR[rst['result']]
				break
	if ok:
		contestsubmission.result = "答案正确"
		contestsubmission.problem.save()
		print(contestsubmission.contestuser.ac_num)
		if contestsubmission.problem not in contestsubmission.contestuser.ac_problems.all():
			contestsubmission.contestuser.ac_problems.add(contestsubmission.problem)
			contestsubmission.contestuser.ac_num += 1
			contestsubmission.contestuser.save()

	contestsubmission.time = maxtime+15
	contestsubmission.memory = maxmemory
	contestsubmission.save()
	return True
