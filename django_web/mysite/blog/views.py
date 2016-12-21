#coding=utf-8

import os
import sys
import socket
import datetime

from django.shortcuts import render,get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect

from blog.models import Essay,EssayType,Archive,Comment
import config_web as cfg_w

#欢迎页
@csrf_protect
def index(request, pageNo=None, etype=None, keyword=None):
	try:
		#文章分页后的页数
		pgNo=int(pageNo)
	except:
		pgNo=1
	try:
		etype=int(etype)
	except:
		etype=None

	if etype:
		#查询该类别的文章，exclude表示not in或者!=
		datas=Essay.objects.all().filter(eType=etype).exclude(title='welcome')
	elif keyword:
		#根据关键字查询,title__contains表示Sql like %+keyword+%
		#Q对象表示Sql关键字OR查询
		#详细的介绍http://docs.djangoproject.com/en/1.0/topics/db/queries/#complex-lookups-with-q-objects
		datas=Essay.objects.all().get(Q(title__contains=keyword)|
									  Q(abstract__contains=keyword)).exclude(title='welcome')
	else:
		#查询所有文章
		datas=Essay.objects.all().exclude(title='welcome')
	#最近的5篇文章
	recentList=datas[:5]
	#数据分页
	paginator = Paginator(datas, 10)
	if pgNo==0:
		pgNo=1
	if pgNo>paginator.num_pages:
		pgNo=paginator.num_pages
	curPage=paginator.page(pgNo)
	#返回到mian.html模板页
	return render(request, 'main.html',{'csrfmiddlewaretoken': 'random string',
										   'page':curPage,
										   'essay_type':EssayType.objects.all(),
										   'pcount':paginator.num_pages,
										   'recent':recentList,
										   'archives':Archive.objects.all(),
										   'welcome':Essay.objects.filter(title='welcome')[0]}
										   	)

#文章详细信息
@csrf_protect
def essay_details(request,eid=None):
	#返回文章详细信息或者404页面
	essay=get_object_or_404(Essay,id=eid)
	recentList=Essay.objects.all()[:5]
	#新用户的Session
	if request.session.get('e'+str(eid),True):
		request.session['e'+str(eid)]=False
		#这里可以用一个timer实现，浏览次数保存在内存中，
		#timer定期将浏览次数提交到数据库
		#文章浏览次数+1
		essay.view_count=essay.view_count+1
		essay.save()
	return render(request, 'details.html',{'csrfmiddlewaretoken': 'random string',
												  'essay':essay,
												  'essay_type':EssayType.objects.all(),
												   'archives':Archive.objects.all(),
												  'date_format':essay.pub_date.strftime('%A %B %d %Y').split(),
												  'recent':recentList
												  })
def leave_comment1(request,eid=None):
	if request.method == 'POST' and eid:
		uname=request.POST.get('uname',None)
		content=request.POST.get('comment',None)
		email=request.POST.get('email',None)
		essay=Essay.objects.get(id=eid)
		Dic_Run = {}
		Dic_Run[cfg.CMD] = 'deployConsole'
		Dic_Run[cfg.CTR] = 'PD'
		return HttpResponse(Ecall(**Dic_Run))
	return HttpResponse(cfg.SYS_WINDOWS)

@csrf_protect
def task(request):
	if request.method == 'POST':
		#从POST请求中获取查询关键字
		rsp = ''
		cmdline=request.POST.get('keyword',None)
		print('web req cmd :%s'%(cmdline))
		task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), cmd='', cmdline=cmdline.strip())
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genNtfHead() + task_info.encode() + cfg.TIP_INFO_EOF)
			rsp = sock.recv(8192)
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print((traceback.format_exc()))
#		return HttpResponse(task_info.encode())
		return HttpResponse(rsp)
	else:
		return index(request)


@csrf_protect
def query(request):
	if request.method == 'POST':
		#从POST请求中获取查询关键字
		cmdline=request.POST.get('keyword',None)
		req_info = ReqInfo(0, 1)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print((traceback.format_exc()))
		return HttpResponse(rsp)
	else:
		return index(request)

#根据关键字来搜索文章
def search(request):
	if request.method == 'POST':
		#从POST请求中获取查询关键字
		key=request.POST.get('keyword',None)
		print(task_info.encode())
		return index(request,keyword=key)
	else:
		return index(request)


#存储用户留言信息
def leave_comment(request,eid=None):
	if request.method == 'POST' and eid:
		uname=request.POST.get('uname',None)
		content=request.POST.get('comment',None)
		email=request.POST.get('email',None)
		essay=Essay.objects.get(id=eid)
		if uname and content and email and essay:
			comment=Comment()
			comment.uname=uname
			comment.content=content
			comment.email=email
			comment.essay=essay
			comment.pub_date=datetime.datetime.now()
			comment.save()
			return essay_details(request,eid)
		return index(request)

	return index(request)

@csrf_protect
def alogin(request):
	errors= []
	account=None
	password=None
	if request.method == 'POST' :
		if not request.POST.get('account'):
			errors.append('Please Enter account')
		else:
			account = request.POST.get('account')
		if not request.POST.get('password'):
			errors.append('Please Enter password')
		else:
			password= request.POST.get('password')
		if account is not None and password is not None :
			user = auth.authenticate(username=account, password=password)
			if user is not None:
				if user.is_active:
					auth.login(request, user)
					return HttpResponseRedirect('/')
				else:
					errors.append('disabled account')
			else :
				errors.append('invaild user')
	return render(request, 'login.html', {'csrfmiddlewaretoken': 'random string', 'errors': errors})

@csrf_protect
def register(request):
	errors= []
	account=None
	password=None
	password2=None
	email=None
	CompareFlag=False

	if request.method == 'POST':
		if not request.POST.get('account'):
			errors.append('Please Enter account')
		else:
			account = request.POST.get('account')
		if not request.POST.get('password'):
			errors.append('Please Enter password')
		else:
			password = request.POST.get('password')
		if not request.POST.get('password2'):
			errors.append('Please Enter password2')
		else:
			password2 = request.POST.get('password2')
		if not request.POST.get('email'):
			errors.append('Please Enter email')
		else:
			email= request.POST.get('email')

		if password is not None and password2 is not None:
			if password == password2:
				CompareFlag = True
			else :
				errors.append('password2 is diff password ')


		if account is not None and password is not None and password2 is not None and email is not None and CompareFlag:
			userlist = User.objects.all()
			try:
				user=User.objects.create_user(account, email, password)
			except IntegrityError as e:
				return HttpResponse(e)
			else:
				user.is_active=True
				user.save
				return HttpResponseRedirect('/account/login/')

	return render(request, 'register.html', {'csrfmiddlewaretoken': 'random string', 'errors': errors})

def alogout(request):
	auth.logout(request)
	return HttpResponseRedirect('/')