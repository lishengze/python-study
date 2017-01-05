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

console_path = cfg_w.CONSOLE_WORK_PATH
if console_path not in sys.path:
	sys.path.append(console_path)

import config as cfg
from ecall import *
from verControl import *
from taskinfo import *

import json
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
###执行即时任务
def task_rpc(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		rsp = ''
		#cmdline=request.POST.get('keyword',None)
		cmdline = '--cmd info'
		cmd = 'info'
		print('web req cmd :%s'%(cmdline))

		#if cmdline.find(cfg.SEMICOLON) != -1:
		#	task_type, cmdline = cmdline.split(cfg.SEMICOLON)  ##命令行中有分号
		#else:
		#	task_type = cfg.TASK_TYPE_ECALL
		task_type = cfg.TASK_TYPE_ECALL
		task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=0, \
			cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genRpcHead() + task_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
	else:
		return index(request)

###执行计划任务
@csrf_protect
def task_ntf(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		rsp = ''
		#cmdline=request.POST.get('keyword',None)
		cmdline = '--cmd info'
		cmd = 'info'
		tasktime = int(time.time()) + 1800

		print('web req cmd :%s'%(cmdline))
		if cmdline.find(cfg.SEMICOLON) != -1:
			task_type, cmdline = cmdline.split(cfg.SEMICOLON)  ##命令行中有分号
		else:
			task_type = cfg.TASK_TYPE_ECALL
		task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=tasktime, \
			cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genNtfHead() + task_info.encode() + cfg.TIP_INFO_EOF)
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print((traceback.format_exc()))
		return HttpResponse(task_info.encode())
	else:
		return index(request)

###查询计划任务状态
@csrf_protect
def query_all_srvstatus(request):
	#if request.method == 'POST':
	if request.method != '':
		#从POST请求中获取查询关键字
		###
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_SRVSTATUS)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			sock.close()
			rsp_list = rsp.split("\n")
			SrvStatus_list = []
			for token in rsp_list:
				if token.startswith(cfg.TIP_BODY_REQ):
					info = token[len(cfg.TIP_BODY_REQ):]
					srv_status = SrvStatus()
					srv_status.decode(info)
					SrvStatus_list.append(srv_status)
			for info in SrvStatus_list:
				print(info.encode())

		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
	else:
		return index(request)

###查询计划任务列表
@csrf_protect
def query_all_tasklist(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		###
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKLIST)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			rsp_list = rsp.split("\n")
			task_list = []
			for token in rsp_list:
				if token.startswith(cfg.TIP_INFO_TASK):
					info = token[len(cfg.TIP_INFO_TASK):]
					task_info = TaskInfo()
					task_info.decode(info)
					task_list.append(task_info)
			for info in task_list:
				print(info.encode())
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
	else:
		return index(request)

###查询计划任务列表结果
@csrf_protect
def query_all_taskresult(request):
	#if request.method == 'POST':
	if request.method != '':
		#从POST请求中获取查询关键字
		###
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKRESULT)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
	else:
		return index(request)

###查询版本信息
def query_all_version(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		###
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_VERSION)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			print 'All Version Rsp: '
			print rsp
			print 'End!'
			sock.close()
			rsp_list = rsp.split("\n")
			version_list = []
			for token in rsp_list:
				if token.startswith(cfg.TIP_BODY_VERINFO):
					info = token[len(cfg.TIP_BODY_VERINFO):]
					version_info = VersionInfo()
					version_info.decode(info)
					version_list.append(version_info)
			for info in version_list:
				print(info.version)
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
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

def is_ajax_request(path):
	path_array = path.split('/')
	ajax_flag = 'AJAX'
	if ajax_flag in path_array:
		return True
	else:
		return False

def is_static_file(file_name):
	name_array = file_name.split('/')
	static_flag = 'static'
	if static_flag in name_array:
		return True
	else:
		return False

def delete_headend_slash(strvalue):
	str_start_index = 0
	str_end_index = len(strvalue)
	if strvalue[str_start_index] == '/':
		str_start_index = 1
	if strvalue[str_end_index-1] == '/':
		str_end_index -= 1
	return strvalue[str_start_index:str_end_index]

def get_static_file_name(origin_file_name):
	name_array = origin_file_name.split('/')
	index = 0
	static_flag = 'static'
	for value in name_array:
		if value == static_flag:
			break
		index += 1
	trans_file_name = '/'.join(name_array[index:])
	return delete_headend_slash(trans_file_name)

def get_html_file_name(path):
	name_array = path.split('/')
	return name_array[len(name_array)-1]

def get_file_name(path):
	file_name = delete_headend_slash(path)
	js_flag = '.js'
	css_flag = '.css'
	html_flag = '.html'
	if file_name[-3:] == js_flag or file_name[-4:] == css_flag:
		if is_static_file(file_name):
			file_name = get_static_file_name(file_name)
	elif file_name[-5:] == html_flag:
		file_name = get_html_file_name(file_name)
	else:
		file_name += html_flag	
	return file_name

def get_ajax_request_name(path):
	name_array = path.split('/')
	ajax_flag = 'AJAX'
	index = 0
	for value in name_array:
		if value == ajax_flag:
			break
		index += 1
	ajax_request_name = '/'.join(name_array[index+1:])
	return delete_headend_slash(ajax_request_name)	

def get_ajax_func(path):
	ajax_name = get_ajax_request_name(path)
	print 'ajax_name: ' + ajax_name
	ajax_func_dict = {
		'Request_All_SrvStatus': test_all_srvstatus,
		'Request_All_TaskList': test_all_tasklist,
		'Request_All_TaskResult': test_all_taskresult,
		'Request_All_Version': test_all_version		
	}
	ajax_func = ajax_func_dict.get(ajax_name, default_ajax_request)
	return ajax_func

def main_query_rsp(request):
	if is_ajax_request(request.path):
		print '\nIs AJAX Request'
		ajax_func = get_ajax_func(request.path)
		return ajax_func(request)		
	else:
		print '\nIs not AJAX Request'
		file_name = get_file_name(request.path)
		print 'file name: ' + file_name + '\n'
		return render(request, file_name)
	return render(request, file_name)

def default_ajax_request(request):
	return HttpResponse(json.dumps({'data':'AJAX Request Failed!'}), content_type = "application/json")

def test_all_srvstatus(request):
	if request.method != '':
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_SRVSTATUS)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			print 'Test_all_srvstatus'
			print rsp
			sock.close()
			rsp_list = rsp.split("\n")
			SrvStatus_list = []
			for token in rsp_list:
				if token.startswith(cfg.TIP_BODY_REQ):
					info = token[len(cfg.TIP_BODY_REQ):]
					srv_status = SrvStatus()
					srv_status.decode(info)
					SrvStatus_list.append(srv_status.__dict__)
			# for info in SrvStatus_list:
			# 	print(info.encode())
			rsp_data = SrvStatus_list
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		# return HttpResponse(json.dumps(rsp_data), content_type = "application/json")
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response
	else:
		return index(request)

def test_all_tasklist(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		###
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKLIST)
		rsp_data = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			print rsp
			rsp_list = rsp.split("\n")
			task_list = []
			for token in rsp_list:
				if token.startswith(cfg.TIP_INFO_TASK):
					info = token[len(cfg.TIP_INFO_TASK):]
					task_info = TaskInfo()
					task_info.decode(info)
					task_list.append(task_info.__dict__)
			# for info in task_list:
			# 	print(info.encode())
			sock.close()
			rsp_data = task_list
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		# return HttpResponse(json.dumps(rsp_data), content_type = "application/json")
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response
	else:
		return index(request)

def test_all_taskresult(request):
	if request.method != '':
		print 'test_all_taskresult!'
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKRESULT)
		task_result = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			task_result = recv_end(sock)
			task_result.split('\n')
			print task_result
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(task_result)
	else:
		return index(request)

def test_all_version(request):
	if request.method != '':
		print '\n+++++ Test_all_version START! +++++'
		print request
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_VERSION)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			tcp_send_head = genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF

			print 'sock send info: '
			print tcp_send_head + '\n'

			rsp = recv_end(sock)
			sock.close()
			rsp_list = rsp.split("\n")
			version_list = []

			for token in rsp_list:
				if token.startswith(cfg.TIP_BODY_VERINFO):
					info = token[len(cfg.TIP_BODY_VERINFO):]
					version_info = VersionInfo()
					version_info.decode(info)
					version_list.append(version_info.__dict__)
			# if info in version_list:
			# 	print info
			rsp_data = version_list
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())

		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response
	else:
		return index(request)

def query_static_src(request):
	path_name = request.path
	print path_name
	path_array = path_name.split('/')
	static_index = 0
	for value in path_array:
		if (value == 'static'):
			break
		static_index += 1
	static_file_name = r'/'.join(path_array[static_index:])
	print static_file_name
	return render(request, static_file_name)



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
