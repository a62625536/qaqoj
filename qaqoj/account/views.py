from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django import forms
from django.contrib.auth.models import User
from .models import MyUser
from django.contrib.auth import authenticate,login,logout

#注册表单
class RegisterForm(forms.ModelForm):
	pw1 = forms.RegexField('^.*$',min_length=8,max_length=20,error_messages={'min_length': '密码长度不能小于8个字符','max_length': '密码长度不能大于20个字符'})
	pw2 = forms.CharField()
	email = forms.EmailField()
	class Meta:
		model = User
		fields = {'username','pw1','pw2','email'}

#业务逻辑：注册
def getRegister(request):
	if request.user.is_authenticated:#用户已登录
		return redirect('/')
	else:#用户未登录
		if request.method == "POST":#POST请求
			username = request.POST.get('username')
			pw1 = request.POST.get('pw1')
			pw2 = request.POST.get('pw2')
			email = request.POST.get('email')
			uf = RegisterForm(request.POST)
			if uf.is_valid():#表单有效
				if pw1 != pw2:#两次密码不同
					return render(request,"account_register.html",{'info':"两次密码不一致!",'username':username,'pw1':pw1,'pw2':pw2,'email':email}) 
				else:#两次密码相同
					user = User()
					user.username = username
					user.email = email
					user.set_password(pw1) 
					user.save()
					myuser = MyUser()
					myuser.user_id = user.id
					myuser.save()
					user = authenticate(username=username,password=pw1)
					login(request,user)
					return redirect('/')
			else:#表单无效
				return render(request,"account_register.html",{'errors':uf.errors,'username':username,'pw1':pw1,'pw2':pw2,'email':email})
		else:#GET请求
			return render(request,'account_register.html')

#业务逻辑：登录
def getLogin(request):
	if request.user.is_authenticated:#用户已登录
		return redirect('/')
	else:#用户未登录
		if request.method == "POST":#POST请求
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(username=username,password=password)
			if user and user.is_active: #帐号密码通过验证
				login(request,user)
				try:
					myuser = MyUser.objects.get(user=request.user)
				except:
					myuser = MyUser()
					myuser.user_id = user.id
					myuser.save()
				return redirect('/')
			else:#帐号密码未通过验证
				return render(request,"account_login.html",{'info':"帐号或密码错误",'username':username,'password':password})
		else:#显示登录页面
			return render(request,'account_login.html')

#业务逻辑：登出
def getLogout(request):
	if request.user.is_authenticated:#用户已登录
		logout(request)
		return redirect('/')
	else:#用户未登录
		return redirect('/')

#邮箱表单
class MailForm(forms.ModelForm):
	email = forms.EmailField()
	class Meta:
		model = User
		fields = {'email'}

#密码表单
class PwForm(forms.ModelForm):
	pw = forms.CharField()
	pw1 = forms.RegexField('^.*$',min_length=8,max_length=20,error_messages={'min_length': '密码长度不能小于8个字符','max_length': '密码长度不能大于20个字符'},)
	pw2 = forms.CharField()
	class Meta:
		model = User
		fields = {'pw','pw1','pw2'}

#业务逻辑：显示用户主页
def getUserHome(request,user_id):
	try:#判断目标用户是否存在
		myuser = MyUser.objects.get(user_id=user_id)
	except:
		return redirect('/')
	if not request.user.is_authenticated or request.user.id != user_id:#访客用户与目标用户不一致
		return render(request,'account_userhome.html',{'myuser':myuser,'userok':False})
	else:#访客用户与目标用户一致
		if request.method == "POST":#POST请求
			if len(request.POST) == 1:#请求修改邮箱
				uf = MailForm(request.POST)
				if uf.is_valid():#新邮箱有效
					myuser.user.email = request.POST.get('email')
					myuser.user.save()
					return render(request,'account_userhome.html',{'myuser':myuser,'userok':True,'info1':"修改邮箱成功!"})
				else:#新邮箱无效
					return render(request,"account_userhome.html",{'myuser':myuser,'userok':True,'errors':uf.errors})
			else:#请求修改密码
				pw = request.POST.get('pw')
				pw1 = request.POST.get('pw1')
				pw2 = request.POST.get('pw2')
				uf = PwForm(request.POST)
				user = authenticate(username=request.user.username,password=pw)
				if user:#旧密码通过验证
					if uf.is_valid():#表单有效
						if pw1 != pw2:#两次密码不同
							return render(request,"account_userhome.html",{'myuser':myuser,'userok':True,'info2':"两次密码不一致!"}) 
						else:#两次密码相同
							user.set_password(pw1)
							user.save()
							user = authenticate(username=user.username,password=pw1)
							login(request,user)
							return render(request,"account_userhome.html",{'myuser':myuser,'userok':True,'info2':"修改密码成功!"}) 
					else:#表单无效
						return render(request,'account_userhome.html',{'myuser':myuser,'userok':True,'errors':uf.errors})
				else:#旧密码未通过验证
					return render(request,'account_userhome.html',{'myuser':myuser,'userok':True,'info2':"密码错误!"})
		else:#GET请求
			return render(request,'account_userhome.html',{'myuser':myuser,'userok':True})