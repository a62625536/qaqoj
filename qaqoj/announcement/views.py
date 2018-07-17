from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from .models import Announcement

#业务逻辑：显示公告列表
def showAnnouncementList(request):
	announcements_all = Announcement.objects.all()
	paginator = Paginator(announcements_all,20)
	page_num = request.GET.get('page',1)
	announcements = paginator.get_page(page_num)
	page_num = announcements.number
	page_range = range(max(1,page_num-2),min(page_num+3,paginator.num_pages+1))
	return render(request,'home.html',{'announcements':announcements,'page_range':page_range})

#业务逻辑：添加公告
def addAnnouncement(request):
	if not request.user.is_superuser:#用户不是超级管理员
		return redirect('/')
	else:#用户是超级管理员
		if request.method == "POST":#POST请求
			announcement = Announcement()
			announcement.title = request.POST.get('title')
			announcement.content = request.POST.get('content')
			announcement.save()
			return redirect('/')
		else:#GET请求
			return render(request,"announcement_add.html")

#业务逻辑：显示公告
def showAnnouncement(request,announcement_id):
	try:#判断目标公告是否存在
		announcement = Announcement.objects.get(pk=announcement_id)
	except:
		return redirect('/')
	if announcement.visible or request.user.is_superuser:#目标公告可见或用户是超级管理员
		return render(request,'announcement.html',{'announcement':announcement})
	else:#目标公告不可见
		return redirect('/')

#业务逻辑：更新公告
def updateAnnouncement(request,announcement_id):
	try:#判断目标公告是否存在
		announcement = Announcement.objects.get(pk=announcement_id)
	except:
		return redirect('/')
	if not request.user.is_superuser:#用户不是超级管理员
		return redirect('/')
	else:#用户是超级管理员
		if request.method == "POST":#POST请求
			announcement.title = request.POST.get('title')
			announcement.content = request.POST.get('content')
			if len(request.POST) == 3:
				announcement.visible = True
			else:
				announcement.visible = False
			announcement.save()
			return redirect('/announcement/'+str(announcement.id))
		else:#GET请求
			return render(request,'announcement_update.html',{'announcement':announcement})

