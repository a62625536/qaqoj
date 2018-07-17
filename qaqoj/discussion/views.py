from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from .models import Discussion

#业务逻辑：显示讨论列表
def showDiscussionList(request):
	discussion_all = Discussion.objects.all()
	paginator = Paginator(discussion_all,10)
	page_num = request.GET.get('page',1)
	discussion = paginator.get_page(page_num)
	page_num = discussion.number
	page_range = range(max(1,page_num-2),min(page_num+3,paginator.num_pages+1))
	return render(request,'discussion_list.html',{'discussion':discussion,'page_range':page_range})

#业务逻辑：增加讨论
def addDiscussion(request):
	if not request.user.is_authenticated:#用户未登录
		return redirect('/login')
	else:#用户已登录
		if request.method == "POST":#POST请求
			discussion = Discussion()
			discussion.user = request.user
			discussion.content = request.POST.get('discussion')
			discussion.save()
			return redirect('/discussions')
		else:#GET请求
			return render(request,'discussion_add.html')
				
#业务逻辑：修改讨论
def editDiscussion(request,dis_id):
	try:#判断目标讨论是否存在
		dis = Discussion.objects.get(pk=dis_id)
	except:
		return redirect('/discussions')
	if not request.user.is_superuser:#用户不是超级管理员
		return redirect('/discussions')
	else:#用户是超级管理员
		if request.method == "POST":#POST请求
			if len(request.POST) == 2:
				dis.visible = True
			else:
				dis.visible = False
			dis.content = request.POST.get('content')
			dis.save()
			return redirect('/discussions')
		else:#GET请求
			return render(request,'discussion_edit.html',{'dis':dis})

