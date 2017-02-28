#coding=utf-8

import os
import sys
import socket
import datetime
import time
import threading

from django.shortcuts import render,get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

from blog.models import Essay,EssayType,Archive,Comment
import config_web as cfg_w
import types

console_path = cfg_w.CONSOLE_WORK_PATH
if console_path not in sys.path:
	sys.path.append(console_path)

import config as cfg
from ecall import *
from verControl import *
from taskinfo import *

import json
from models import Person
from models import GroupInfo
from models import UserInfo
import shutil

reload(sys)
sys.setdefaultencoding('utf8')

g_users = {}
g_groups = {}
g_chosen_user = {}
g_chosen_group = {}
g_login_user = {}
g_env_array = []
g_get_html_object = {}
g_group_permission = []
g_user_permission = []

# ENV_KEY = 'PTEST_170'
ENV_KEY = 'TEST_170'

class User(object):
	def __init__(self, name = 'tmp', email = 'tmp', permisson = 'all', groups = 'all', password = 'tmp'):
		self.name = name
		self.email = email
		self.permisson = permisson
		self.groups = groups
		self.password = password
		self.__dict__ = {
			'name': self.name,
			'email': self.email,
			'permisson': self.permisson,
			'groups': self.groups,
			'password': self.password
		}

class Group(object):
	def __init__(self, name = 'tmp', permisson = 'all'):
		self.name = name
		self.permisson = permisson
		self.__dict__ = {
			'name': self.name,
			'permisson': self.permisson
		}

class RpcResult(object):
	def __init__(self, data_type, data_array):
		if data_type == 'default':
			self.__dict__ = {
				'object_info': data_array[0],
				'ip_address': data_array[1],
				'cmd_line': ' '.join(data_array[2:])
			}
		if data_type == 'relay':
			self.__dict__ = {
				'origin_ip_address': data_array[0],
				'relay_relation': data_array[1],
			}
		if data_type == 'host':
			self.__dict__ = {
				'ip_address': data_array[0],
				'os_type': data_array[1],
				'host_name': data_array[2]
			}
		if is_version_control_req(data_type):
			if data_type.find('show')!= -1:
				self.__dict__ = {
					'SEQ': data_array[0],
					'version': data_array[1],
					'datetime': data_array[2],
					'status': data_array[3]
				}
			else:
				self.__dict__ = {
					'info': data_array
				}

def init_globals():
	global g_users, g_groups, g_login_user, \
		   g_env_array, g_get_html_object, \
		   g_group_permission, g_user_permission

	Trump = User('Trump', 'Trump@gmail.com')
	Clinton = User('Clinton', 'Clinton@gmail.com')
	Obama = User('Obama', 'Obama@gmail.com')
	Bush = User('Bush', 'Bush@gmail.com')
	g_users = [Trump, Clinton, Obama, Bush]
	g_chosen_user = Trump

	# communist_party = Group('共产党')
	# democratic_party = Group('民主党')
	# republican_party = Group('共和党')
	communist_party = Group('Communist Party')
	democratic_party = Group('Democratic Party')
	republican_party = Group('Republican Party')
	g_groups = [communist_party, democratic_party, republican_party]

	g_chosen_group = republican_party
	g_login_user = User('SHFE.SFIT', 'SHFE.SFIT@hotmail.com')

	g_group_permission = ["admin | log entry | Can change log entry", \
						  "admin | log entry | Can add log entry", \
						  "admin | log entry | Can delete log entry", \
						  "auth | group | Can add group", \
						  "auth | group | Can change group", \
						  "auth | group | Can delete group", \
						  "auth | permission | Can add permission", \
						  "auth | permission | Can change permission", \
						  "auth | permission | Can delete permission", \
						  "auth | user | Can add user", \
						  "auth | user | Can change user", \
						  "auth | user | Can delete user", \
						  "contenttypes | content type | Can add content type", \
						  "contenttypes | content type | Can change content type", \
						  "contenttypes | content type | Can delete content type", \
						  "sessions | session | Can add session", \
						  "sessions | session | Can change session", \
						  "sessions | session | Can delete session"]
	g_user_permission = g_group_permission

	for value in cfg_w.ENV_DICT:
		g_env_array.append(value)
	# print 'g_env_array: '
	# print g_env_array

init_globals()

def sock_conn(key):
	daemaon_ip = cfg_w.ENV_DICT[key][1]
	daemon_port = cfg_w.ENV_DICT[key][2]
	print(key, daemaon_ip, daemon_port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((daemaon_ip, daemon_port))
	except Exception:
		print(traceback.format_exc())
		sock = sock_conn(key)
	return sock

def getKey(key):
	daemaon_ip = cfg_w.ENV_DICT[key][1]
	daemon_port = cfg_w.ENV_DICT[key][2]
	print(key, daemaon_ip, daemon_port)
	return daemaon_ip, daemon_port

def sock_conn(daemaon_ip, daemon_port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((daemaon_ip, daemon_port))
	except Exception:
		print(traceback.format_exc())
		sock = sock_conn(daemaon_ip, daemon_port)
	return sock

def is_version_control_req(data_type):
	if data_type.find('version_control') != -1:
		return True
	else:
		return False

def uploadFile(sock, FileSrc, FileDst):
	try:
		file_md5 = md5sum(FileSrc)
		filename = os.path.basename(FileSrc)
		f = open(FileSrc, 'rb')
		sock.send(genFileHead(filename, file_md5, FileDst))
		bytes = 0
		while 1:
			fileinfo = f.read(cfg.DEFAULT_RECV)
			if not fileinfo:
				break
			bytes = bytes + len(fileinfo)
			#print('Send ' + str(bytes) + ' bytes ...')
			sock.send(fileinfo)
			#time.sleep(0.001)
		sock.send(cfg.TIP_INFO_EOF)
		rtn = cfg.CMD_SUCC
	except Exception as e:
		rtn = cfg.CMD_FAIL
		print(traceback.format_exc())
	finally:
		return rtn

def downloadFile(sock, FileSrc, FileDst):
	try:
		sock.send(genFReqHead(FileSrc) + cfg.TIP_INFO_EOF)
		rsp = recv_end(sock)
		head_info, buf = getFRspHead(rsp)
		print(head_info)
		print('++++++++')
		print(buf)
		seq_id, filename, status = getFRspInfo(head_info.strip())
		print(filename, status)
		if int(status) == cfg.CMD_SUCC:
			## dir exsit?
			f = open(FileDst, 'w')
			f.write(buf)
			f.close()
			rtn = cfg.CMD_SUCC
		else:
			rtn = cfg.CMD_FAIL
	except Exception as e:
		rtn = cfg.CMD_FAIL
		print(traceback.format_exc())
	finally:
		return rtn

def output_msg(description, info, *other_info):
	print description
	print info
	for value in other_info:
		print value
	print ''

@csrf_protect
def update_srv(request):
	rsp = ''
	if request.method == "POST":
		start_time = int(time.time())
		myFile = request.FILES.get("myfile", None)
		if not myFile:
			return HttpResponse("no files for upload!")
		filepath = os.path.join(cfg.WORK_PATH_TEMP, myFile.name)
		filedst = os.path.join(cfg.WORK_PATH_UPDATE, myFile.name)
		destination = open(filepath,'wb+')
		for chunk in myFile.chunks():
			destination.write(chunk)
		destination.close()
		daemaon_ip, daemon_port = getKey(ENV_KEY)
		sock = sock_conn(daemaon_ip, daemon_port)
		rtn = uploadFile(sock, filepath, filedst)
		end_time = int(time.time())
		if rtn == cfg.CMD_SUCC:
			rsp = recv_end(sock)
			info = '<br/>File transfer SUCC, cost ' + str(end_time - start_time) + ' secs.'
		else:
			info = '<br/>File transfer FAIL, cost ' + str(end_time - start_time) + ' secs.'
		rsp = rsp + info
		sock.close()
		return HttpResponse(rsp)
	else:
		return index(request)

@csrf_protect
def upload_file(request):
	rsp = ''
	if request.method == "POST":
		start_time = int(time.time())
		myFile = request.FILES.get("myfile", None)
		if not myFile:
			return HttpResponse("no files for upload!")
		filepath = os.path.join(cfg.WORK_PATH_TEMP, myFile.name)
		filedst = filepath + cfg.DOT + cfg.PID
		destination = open(filepath,'wb+')
		for chunk in myFile.chunks():
			destination.write(chunk)
		destination.close()
		daemaon_ip, daemon_port = getKey(ENV_KEY)
		sock = sock_conn(daemaon_ip, daemon_port)
		rtn = uploadFile(sock, filepath, filedst)
		end_time = int(time.time())
		if rtn == cfg.CMD_SUCC:
			rsp = recv_end(sock)
			info = '<br/>File transfer SUCC, cost ' + str(end_time - start_time) + ' secs.'
		else:
			info = '<br/>File transfer FAIL, cost ' + str(end_time - start_time) + ' secs.'
		rsp = rsp + info
		sock.close()
		return HttpResponse(rsp)
	else:
		return index(request)

@csrf_protect
###执行即时任务
def download_file(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		FileName = request.POST.get('filename',None)
		if not FileName:
			return HttpResponse("no files for request!")
		daemaon_ip, daemon_port = getKey(ENV_KEY)
		sock = sock_conn(daemaon_ip, daemon_port)
		FileSrc = FileName
		FileDst = os.path.join(cfg.WORK_PATH_TEMP, FileName)
		FileNew = FileDst + cfg.DOT +cfg.PID
		FileNewDst = os.path.join(cfg.WORK_PATH_CFG, FileName + cfg.DOT + cfg.PID)
		rtn = downloadFile(sock, FileSrc, FileDst)
		sock.close()
		if rtn == cfg.CMD_SUCC:
			daemaon_ip, daemon_port = getKey(ENV_KEY)
			sock = sock_conn(daemaon_ip, daemon_port)
			shutil.copyfile(FileDst, FileNew)
			f = open(FileNew, "a+")
			f.write("## Add Test Info by " + str(cfg.PID) + ' \n')
			f.close()
			uploadFile(sock, FileNew, FileNewDst)
			result_info = " SUCC"
			sock.close()
		else:
			result_info = " FAILED"

		return HttpResponse("Download " + FileName + result_info)
	else:
		return index(request)

class ViewMain(object):
	def __init__(self):
		self.name = "ViewMain"
		self._ajax_func = AjaxReqFunc()
		self._get_html_object = GetHtmlObject()

	def is_ajax_request(self, path):
		path_array = path.split('/')
		ajax_flag = 'AJAX'
		if ajax_flag in path_array:
			return True
		else:
			return False

	def is_static_file(self, fileName):
		name_array = fileName.split('/')
		static_flag = 'static'
		if static_flag in name_array:
			return True
		else:
			return False

	def delete_headend_slash(self, strvalue):
		str_start_index = 0
		str_end_index = len(strvalue)
		if strvalue[str_start_index] == '/':
			str_start_index = 1
		if strvalue[str_end_index-1] == '/':
			str_end_index -= 1
		return strvalue[str_start_index:str_end_index]

	def get_static_fileName(self, origin_fileName):
		name_array = origin_fileName.split('/')
		index = 0
		static_flag = 'static'
		for value in name_array:
			if value == static_flag:
				break
			index += 1
		trans_fileName = '/'.join(name_array[index:])
		return self.delete_headend_slash(trans_fileName)

	def get_html_fileName(self, path):
		name_array = path.split('/')
		return name_array[len(name_array)-1]

	def is_empty_html_request(self, fileName):
		name_array = fileName.split('/')
		last_fileName = name_array[len(name_array)-1]
		if last_fileName.find('.') == -1:
			return True
		else:
			return False

	def is_html_request(self, path_name):
		html_flag = '.html'
		flag = False
		if len(path_name) > len(html_flag) and path_name[-len(html_flag):] == html_flag:
			flag = True
		return flag

	def get_fileName(self, path):
		fileName = self.delete_headend_slash(path)
		html_flag = '.html'
		# if is_static_file(fileName):
		# 	fileName = get_static_fileName(fileName)
		if self.is_empty_html_request(fileName):
			fileName += html_flag
		return fileName

	def get_html_fileName_and_id(self, fileName):
		html_flag = '.html'
		fileName = fileName[:len(fileName)-len(html_flag)]
		fileName_array = fileName.split('/')
		print fileName_array
		if fileName_array[len(fileName_array)-1] == 'change' and fileName_array[len(fileName_array)-2].isdigit():
			data_id = fileName_array[len(fileName_array)-2]
			fileName_array.remove(fileName_array[len(fileName_array)-2])
			fileName = '/'.join(fileName_array)
			fileName = self.delete_headend_slash(fileName) + html_flag
			return {
				'id': data_id,
				'fileName': fileName,
			}
		elif fileName_array[len(fileName_array)-1].find('search=') != -1:
			data_id = fileName_array[len(fileName_array)-1][len('search='):]
			fileName_array.remove(fileName_array[len(fileName_array)-1])
			fileName = '/'.join(fileName_array)
			fileName = self.delete_headend_slash(fileName) + html_flag
			return {
				'id': data_id,
				'fileName': fileName,
			}
		else:
			return False

	def get_ajax_request_name(self, path):
		name_array = path.split('/')
		ajax_flag = 'AJAX'
		index = 0
		for value in name_array:
			if value == ajax_flag:
				break
			index += 1
		ajax_request_name = '/'.join(name_array[index+1:])
		return self.delete_headend_slash(ajax_request_name)

	def get_ajax_func(self, path):
		ajax_name = self.get_ajax_request_name(path)
		print 'ajax_name: ' + ajax_name
		ajax_func_dict = {
			'Set_ENV_KEY': self._ajax_func.set_env_key,
			'Request_All_SrvStatus': self._ajax_func.test_all_srvstatus,
			'Request_All_TaskList': self._ajax_func.test_all_tasklist,
			'Request_All_TaskResult': self._ajax_func.test_all_taskresult,
			'Request_All_Version': self._ajax_func.test_all_version,
	        'Request_Task_Rpc': self._ajax_func.test_task_rpc,
	        'Request_Task_Ntf': self._ajax_func.test_task_ntf,
			'Request_Info':self._ajax_func.request_info,
			'Get_NTF_Task_Result': self._ajax_func.get_all_ntf_task_result,
			'Get_NTF_Task_State': self._ajax_func.get_all_ntf_task_state,
			'Upload_File': self._ajax_func.upload_file,
			'Set_DB_Data': self._ajax_func.set_dbdata,
			'Get_DB_Data': self._ajax_func.get_dbdata,
			'Set_Chosen_Group': self._ajax_func.set_chosen_group,
			'Set_Chosen_User': self._ajax_func.set_chosen_user,
			'Delete_Group': self._ajax_func.delete_group_data,
			'Delete_User': self._ajax_func.delete_user_data,
			'Add_User': self._ajax_func.add_user_data,
			'Add_Group': self._ajax_func.add_group_data,
			'Change_User': self._ajax_func.change_user_data,
			'Change_Group': self._ajax_func.change_group_data,
		}
		ajax_func = ajax_func_dict.get(ajax_name, self._ajax_func.default_ajax_request)
		return ajax_func

	def get_file_object(self, fileName, id = -1):
		file_object_dict = {
			'test_req.html': self._get_html_object.get_test_req_object,
			'login.html': self._get_html_object.get_login_object,
			'admin.html': self._get_html_object.get_admin_object,
			'admin/auth.html': self._get_html_object.get_admin_auth_object,
			'admin/logout.html': self._get_html_object.get_admin_logout_object,
			'admin/password_change.html': self._get_html_object.get_admin_password_change_object,
			'admin/auth/group.html': self._get_html_object.get_admin_auth_group_object,
			'admin/auth/group/add.html': self._get_html_object.get_admin_auth_group_add_object,
			'admin/auth/group/change.html': self._get_html_object.get_admin_auth_group_change_object,
			'admin/auth/user.html': self._get_html_object.get_admin_auth_user_object,
			'admin/auth/user/add.html': self._get_html_object.get_admin_auth_user_add_object,
			'admin/auth/user/change.html': self._get_html_object.get_admin_auth_user_change_object,
		}
		object_func = file_object_dict.get(fileName, lambda :{})
		if id !=-1:
			print object_func(id)
			return object_func(id)
		else:
			print object_func()
			return object_func()

	@csrf_exempt
	def main_query_rsp(self, request):
		if self.is_ajax_request(request.path):
			print '\nIs AJAX Request'
			ajax_func = self.get_ajax_func(request.path)
			return ajax_func(request)
		else:
			print '\nIs not AJAX Request'
			print 'request.path: ', request.path
			fileName = self.get_fileName(request.path)
			file_object = {}
			if self.is_html_request(fileName):
				return_data = self.get_html_fileName_and_id(fileName)
				print return_data
				if return_data:
					fileName = return_data['fileName']
					file_object = self.get_file_object(fileName, return_data['id'])
				else:
					file_object = self.get_file_object(fileName)
			print 'file name: ' + fileName + '\n'
			return render(request, fileName, file_object)

class AjaxReqFunc(object):
	def __init__ (self):
		self.name = 'AjaxReqFunc'

	def default_ajax_request(self, request):
		return HttpResponse(json.dumps({'data':'AJAX Request Failed!'}), content_type = "application/json")

	def upload_file(self, request):
		rsp_data = {}
		if request.method == 'POST':
			start_time = int(time.time())
			upload_file = request.FILES['file']
			if upload_file:
				filename = str(upload_file).encode('utf-8')
				filepath = os.path.join(cfg.WORK_PATH_TEMP, filename)
				filedst = filepath + cfg.DOT + cfg.PID
				print 'filepath: ', filepath
				print 'filedest: ', filedst

				destination = open(filepath,'wb+')
				for chunk in upload_file.chunks():
					destination.write(chunk)
				destination.close()
				daemaon_ip, daemon_port = getKey(ENV_KEY)
				sock = sock_conn(daemaon_ip, daemon_port)
				rtn = uploadFile(sock, filepath, filedst)
				end_time = int(time.time())

				status = ''
				upload_time = str(end_time - start_time)
				print 'rtn: ', rtn
				if rtn == cfg.CMD_SUCC:
					rsp = recv_end(sock)
					info = '<br/>File transfer SUCC, cost ' + str(end_time - start_time) + ' secs.'
					status = "Successful"
				else:
					info = '<br/>File transfer FAIL, cost ' + str(end_time - start_time) + ' secs.'
					status = 'Failed'
				rsp = rsp + info
				print rsp
				print 'status: ', status
				sock.close()
				rsp_data = {
					'type': status,
					'upload_time': upload_time
				}
			else:
				rsp_data = {
					'type': 'Failed',
					'info': 'No upload file'
				}
		else:
			rsp_data = {
				'type': 'Failed',
				'info': 'Is Not POST Requset!'
			}
		return HttpResponse(json.dumps(rsp_data), content_type = "application/json")

	def handle_uploaded_file(self, file, filename):
		filename = filename.encode('utf-8')
		print 'filename: ', filename
		if not os.path.exists('upload/'):
			os.mkdir('upload/')
		full_fileName = 'upload/' + filename
		print 'full_fileName: ', full_fileName
		with open(full_fileName, 'wb+') as destination:
			for chunk in file.chunks():
				destination.write(chunk)
		destination.close()
		return full_fileName

	def set_dbdata(self, request):
		tmp_data = Person(name='LSZ', age=27)
		tmp_data.save()

		# for group_data in g_groups:
		# 	print group_data.name
		# 	print group_data.permisson
		# 	db_obj = GroupInfo(name = group_data.name, permission = group_data.permisson)
		# 	db_obj.save()

		for user in g_users:
			db_obj = UserInfo(name = user.name, email=user.email, \
			                  permission = user.permisson, groups = user.groups)
			db_obj.save()
		rsp_data = {'data': 'set database data!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def get_dbdata(self, request):
		# person_obj = Person.objects.all()
		# result = {
		# 	'name': person_obj[0].name,
		# 	'age': person_obj[0].age
		# }

		group_array = []
		group_obj = GroupInfo.objects.all()

		for tmp_obj in group_obj:
			group_array.append(Group(tmp_obj.name, tmp_obj.permission).__dict__)

		rsp_data = {'data': group_array}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def delete_group_data(self, request):
		delete_data = request.POST.getlist('req_json')
		print delete_data
		successful_delete_data = []
		failed_delete_data = []
		for value in delete_data:
			if GroupInfo.objects.filter(name = value).delete():
				successful_delete_data.append(value)
			else:
				failed_delete_data.append(value)

		rsp_data = {'successful': successful_delete_data,
					'failed': failed_delete_data}
		print rsp_data
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def delete_user_data(self, request):
		delete_data = request.POST.getlist('req_json')
		successful_delete_data = []
		failed_delete_data = []
		for value in delete_data:
			if UserInfo.objects.filter(name = value).delete():
				successful_delete_data.append(value)
			else:
				failed_delete_data.append(value)

		rsp_data = {'successful': successful_delete_data,
					'failed': failed_delete_data}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def add_group_data(self, request):
		add_data = request.POST.getlist('req_json')[0]
		trans_add_data = json.loads(add_data)
		print trans_add_data
		status = ''
		if GroupInfo.objects.filter(name = trans_add_data['name']):
			status = 'Failed'
		else:
			add_group = GroupInfo(name = trans_add_data['name'], permission = trans_add_data['permission'])
			add_group.save()
			status = 'Successful'

		rsp_data = {'status': status}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def add_user_data(self, request):
		add_data = request.POST.getlist('req_json')[0]
		trans_add_data = json.loads(add_data)
		print trans_add_data
		status = ''
		error = ''
		if UserInfo.objects.filter(name = trans_add_data['name']):
			status = 'Failed'
			error = '用户已经存在！'
		else:
			add_user = UserInfo(name = trans_add_data['name'], password = trans_add_data['password'])
			add_user.save()
			status = 'Successful'

		rsp_data = {'status': status,
					'error': error}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def change_group_data(self, request):
		change_data = request.POST.getlist('req_json')[0]
		trans_change_data = json.loads(change_data)
		print trans_change_data
		status = ''
		group = GroupInfo.objects.get(name = trans_change_data['name'])
		if group:
			status = 'Successful'
			group.permission = trans_change_data['permission']
			group.save()
		else:
			status = 'Failed'

		rsp_data = {'status': status}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def change_user_data(self, request):
		change_data = request.POST.getlist('req_json')[0]
		trans_change_data = json.loads(change_data)
		print trans_change_data
		status = ''
		user = UserInfo.objects.get(name = trans_change_data['name'])
		if user:
			status = 'Successful'
			user.permission = trans_change_data['permission']
			user.email = trans_change_data['email']
			user.groups = trans_change_data['groups']
			user.save()
		else:
			status = 'Failed'

		rsp_data = {'status': status}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def set_chosen_group(self, request):
		group_name = request.POST.getlist('req_json')[0]
		group_name = group_name.encode('utf-8')
		print 'group_name:   ', group_name
		group = GroupInfo.objects.filter(name = group_name)
		print 'group_id:  ', group[0].id
		rsp_url = ''
		error_info = ''
		if group:
			rsp_url = '/admin/auth/group/' + str(group[0].id) + '/change'
		else:
			error_info = 'request name does not exit!'

		rsp_data = {'data': rsp_url,
					'error': error_info}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def set_chosen_user(self, request):
		userName = request.POST.getlist('req_json')[0]
		userName = userName.encode('utf-8')
		print 'userName:   ', userName
		user = UserInfo.objects.filter(name = userName)[0]
		print 'user_id:  ', user.id
		rsp_url = ''
		error_info = ''
		if user:
			rsp_url = '/admin/auth/user/' + str(user.id) + '/change'
		else:
			error_info = 'request name does not exit!'

		rsp_data = {'data': rsp_url,
					'error': error_info}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def set_env_key(self, request):
		global ENV_KEY
		print 'This is AjaxReqFunc.set_env_key!'
		req_env_key_value = request.POST.getlist('env_key_value')[0]

		ENV_KEY = req_env_key_value
		print 'ENV_KEY: ', ENV_KEY

		rsp_data = {
			'data': req_env_key_value
		}
		response = HttpResponse(json.dumps(rsp_data))
		# response = HttpResponse(req_json)
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def get_task_info(self, trans_req_json):
		task_type = cfg.TASK_TYPE_ECALL
		cmdline = ''
		if 'type' in trans_req_json and trans_req_json['type'] == 'version_control':
			data_type = 'version_control_' + trans_req_json['--cmd']
			task_type = cfg.TASK_TYPE_VERCONTROL
		elif '--args' not in trans_req_json or trans_req_json['--args'] == '' or \
			trans_req_json['--args'] =='app':
			data_type = 'default'
		else:
			data_type = trans_req_json['--args']
		req_para = ['--cmd', '--args', '--grp', \
					'--ctr', '--srv', '--srvno',\
					'--ictr', '--isrv', '--isrvno']
		for value in req_para:
			if value in req_para and value in trans_req_json and trans_req_json[value] !='':
				cmdline += value + ' ' + trans_req_json[value] + ' '

		print '\ndata_type: ', data_type
		print 'task_type: ', task_type
		print ('The REQUEST command line is: %s\n' %(cmdline))
		return {
			'data_type': data_type,
			'task_type': task_type,
			'cmdline': cmdline,
			'cmd': trans_req_json['--cmd']
		}

	@csrf_exempt
	def test_task_rpc(self, request):
		if request.method != '':
			req_json = request.POST.getlist('req_json')[0]
			print req_json
			trans_req_json = json.loads(req_json)
			print trans_req_json

			req_data = self.get_task_info(trans_req_json)
			data_type = req_data['data_type']
			task_type = req_data['task_type']
			cmdline = req_data['cmdline']

			original_rsp_data = ''
			cmd = 'info'
			task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=0, \
						cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
			trans_rsp_data = {}
			try:
				daemaon_ip, daemon_port = getKey(ENV_KEY)
				sock = sock_conn(daemaon_ip, daemon_port)
				sock.send(genRpcHead() + task_info.encode() + cfg.TIP_INFO_EOF)
				original_rsp_data = recv_end(sock)
				sock.close()
				print ('The original rsp data is:\n%s' %(original_rsp_data))
				trans_rsp_data = self.process_rpc_result(original_rsp_data, data_type)
				print 'Transed Rsp Data: '
				print trans_rsp_data
			except Exception as e:
				print('notifyDaemon failed!')
				print(traceback.format_exc())
			rsp_data = trans_rsp_data
			response = HttpResponse(json.dumps(rsp_data))
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "*"
			return response
		else:
			return index(request)

	@csrf_exempt
	def request_info(self, request):
		if request.method != '':
			req_json = request.POST.getlist('req_json')[0]
			trans_req_json = json.loads(req_json)
			output_msg('Original Req_json!', req_json)
			output_msg('Transed Req_Json!', trans_req_json)

			compact_req_json = {}
			for key in trans_req_json:
				if key != 'ENV_KEY' and trans_req_json[key] != '':
					if key.find('--') == 0:
						trans_key = key[2:]
						compact_req_json[trans_key] = trans_req_json[key]
					else:
						compact_req_json[key] = trans_req_json[key]
			# compact_req_json = json.dumps(compact_req_json)
			compact_req_json = str(compact_req_json)
			eval_req_json = eval(compact_req_json)
			output_msg('Str Compact Req_JSON', compact_req_json)

			ENV_KEY = trans_req_json['ENV_KEY']
			req_data = self.get_task_info(trans_req_json)
			data_type = req_data['data_type']
			task_type = req_data['task_type']
			rsp = ''
			original_rsp_data = ''
			trans_rsp_data = {}
			args = 'relay'

			try:
				daemaon_ip, daemon_port = getKey(ENV_KEY)
				sock = sock_conn(daemaon_ip, daemon_port)
				# sock.send(genCmdInfoHead() + args + cfg.TIP_INFO_EOF)
				sock.send(genCmdInfoHead() + compact_req_json + cfg.TIP_INFO_EOF)
				original_rsp_data = recv_end(sock)
				sock.close()
				trans_rsp_data = self.process_rpc_result(original_rsp_data, data_type)

				output_msg('The original rsp data is: ', original_rsp_data)
				output_msg('Transed Rsp Data: ', trans_rsp_data)
			except Exception as e:
				print('notifyDaemon failed!')
				print(traceback.format_exc())

			response = HttpResponse(json.dumps(trans_rsp_data))
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "*"
			return response
		else:
			return index(request)

	def test_task_ntf(self, request):
		if request.method != '':
			req_json = request.POST.getlist('req_json')[0]
			trans_req_json = json.loads(req_json)

			ENV_KEY = trans_req_json['ENV_KEY']
			req_data = self.get_task_info(trans_req_json)
			data_type = req_data['data_type']
			cmdline = req_data['cmdline']
			task_type = req_data['task_type']
			cmd = req_data['cmd']

			output_msg('Original Req_json!', req_json)
			output_msg('Transed Req_Json!', trans_req_json)

			tasktime = int(time.time()) + 1
			task_info = TaskInfo(state = cfg.FLAG_TASK_READY, TID = 0, PID = int(cfg.PID), exec_time=tasktime, \
								 cmd = cmd.strip(), cmdline = cmdline.strip(), task_type = int(task_type))
			# if cmdline.find(cfg.SEMICOLON) != -1:
			# 	task_type, cmdline = cmdline.split(cfg.SEMICOLON)  ##命令行中有分号
			# else:
			# 	task_type = cfg.TASK_TYPE_ECALL
			# 	task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=tasktime, \
			# 						 cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
			try:
				daemaon_ip, daemon_port = getKey(ENV_KEY)
				sock = sock_conn(daemaon_ip, daemon_port)
				sock.send(genNtfHead() + task_info.encode() + cfg.TIP_INFO_EOF)
				sock.close()

				output_msg('task_info: ', task_info.__dict__)
			except Exception as e:
				print('notifyDaemon failed!')
				print((traceback.format_exc()))

			rsp_data = {'task_info': task_info.__dict__,
						'data_type': data_type}
			rsp_data = [task_info.TID, data_type]
			response = HttpResponse(json.dumps(rsp_data))
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "*"
			return response
		else:
			return index(request)

	def test_all_srvstatus(self, request):
		if request.method != '':
			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_SRVSTATUS)
			rsp = ''
			try:
				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
				daemaon_ip, daemon_port = getKey(ENV_KEY)
				sock = sock_conn(daemaon_ip, daemon_port)
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

	def test_all_tasklist(self, request):
		#if request.method == 'POST':
		if request.method != '':

			#从POST请求中获取查询关键字
			###
			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKLIST)
			rsp_data = ''
			try:
				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
				daemaon_ip, daemon_port = getKey(ENV_KEY)
				sock = sock_conn(daemaon_ip, daemon_port)
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

	def test_all_taskresult(self, request):
		if request.method != '':
			print 'test_all_taskresult!'
			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKRESULT)
			task_result = ''
			trans_result = {}
			try:
				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
				daemaon_ip, daemon_port = getKey(ENV_KEY)
				sock = sock_conn(daemaon_ip, daemon_port)
				sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
				task_result = recv_end(sock)
				sock.close()

				task_result = task_result.split('\n')
				trans_result = eval(task_result[1])

				output_msg('Original Rsp Data:', task_result[1], type(task_result[1]))
				output_msg('Transed Rsp Data:', trans_result, type(trans_result))
			except Exception as e:
				print('notifyDaemon failed!')
				print(traceback.format_exc())
			rsp_data = {'task_result': trans_result}
			response = HttpResponse(json.dumps(rsp_data))
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "*"
			return response
		else:
			return index(request)

	def test_all_version(self, request):
		if request.method != '':
			req_data = request.POST.getlist('req_json')[0]
			req_data = json.loads(req_data)
			ENV_KEY = req_data['ENV_KEY']

			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_VERSION)
			rsp = ''
			rsp_data = ''
			try:
				daemaon_ip, daemon_port = getKey(ENV_KEY)
				sock = sock_conn(daemaon_ip, daemon_port)
				sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
				tcp_send_head = genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF

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
				if info in version_list:
					print info
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

	def get_task_result(taskID):
		req_info = ReqInfo(taskID, cfg.FLAG_REQTYPE_TASKRESULT)
		task_result = ''
		try:
			daemaon_ip, daemon_port = getKey(ENV_KEY)
			sock = sock_conn(daemaon_ip, daemon_port)
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			task_result = recv_end(sock)
			sock.close()

			task_result = task_result.split('\n')
			print 'Original Rsp Data:'
			print task_result[1]
			print type(task_result[1])

			trans_result = eval(task_result[1])
			print 'Transed Rsp Data:'
			print trans_result
			print type(trans_result)
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())

		return trans_result

	def get_nft_task_state(self, ENV_KEY, task_id = 0):
		req_info = ReqInfo(task_id, cfg.FLAG_REQTYPE_TASKINFO)
		rsp = ''
		task_list = []
		try:
			daemaon_ip, daemon_port = getKey(ENV_KEY)
			sock = sock_conn(daemaon_ip, daemon_port)
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			print rsp
			rsp_list = rsp.split("\n")
			for token in rsp_list:
				if token.startswith(cfg.TIP_INFO_TASK):
					info = token[len(cfg.TIP_INFO_TASK):]
					task_info = TaskInfo()
					task_info.decode(info)
					if task_id == 0:
						task_list.append(task_info.__dict__)
					else:
						task_list = task_info.__dict__

			if task_id == 0:
				for info in task_list:
					print info
			else:
				print task_list

			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return task_list

	def get_nft_task_result(self, ENV_KEY, task_id = 0):
		req_info = ReqInfo(task_id, cfg.FLAG_REQTYPE_TASKRESULT)
		task_result = ''
		trans_result = {}
		try:
			daemaon_ip, daemon_port = getKey(ENV_KEY)
			sock = sock_conn(daemaon_ip, daemon_port)
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			task_result = recv_end(sock)
			sock.close()
			if task_id == 0:
				task_result = task_result.split('\n')
				trans_result = eval(task_result[1])
				output_msg('Transed Rsp Data:', trans_result, type(trans_result))
				output_msg('Original Rsp Data:', task_result, type(task_result))
			else:
				trans_result = task_result
				output_msg('Transed Rsp Data:', trans_result)
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return trans_result

	###查询所有计划任务
	def get_all_ntf_task_result(self, request):
		if request.method != '':
			req_data = request.POST.getlist('req_json')[0]
			req_data = json.loads(req_data)

			task_data = req_data['task_data']
			ENV_KEY = req_data['ENV_KEY']

			output_msg('req_json', req_data)
			output_msg('task_data', task_data)

			task_type = {}
			task_result = {}

			# 遍历客户请求
			index  = 0
			while index < len(task_data):
				# task_data[index] = task_data[index].split(',')
				task_id = task_data[index][0]
				task_type[task_id] = task_data[index][1]
				task_info = self.get_nft_task_state(ENV_KEY, task_id)
				if task_info == []:
					break
				if task_info['state'] == 3:
					task_result[task_id] = self.get_nft_task_result(ENV_KEY, task_id)
					task_result[task_id] = self.process_rpc_result(task_result[task_id], task_type[task_id])
				else:
					task_result[task_id] = 'Empty'
				index += 1
			output_msg('task_result', task_result)

			# 全遍历
			# task_info = self.get_nft_task_state()
			# for task in task_info:
			# 	task_id = task['TID']
			# 	if task['state'] == 3:
			# 		task_result[task_id] = self.get_nft_task_result(task_id)

			rsp_data = {'task_result': task_result}

			response = HttpResponse(json.dumps(rsp_data))
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "*"
			return response
		else:
			response = HttpResponse(json.dumps('wrong!'))
			return response

	def get_all_ntf_task_state(self, request):
		if request.method != '':
			req_data = request.POST.getlist('req_json')[0]
			req_data = json.loads(req_data)
			ENV_KEY = req_data['ENV_KEY']

			task_info = self.get_nft_task_state(ENV_KEY)
			rsp_data = {'task_info': task_info}
			response = HttpResponse(json.dumps(rsp_data))
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "*"
			return response
		else:
			response = HttpResponse(json.dumps('wrong!'))
			return response

	def process_rpc_result(self, origin_data, data_type):
		failed_data = self.get_rpc_failed_data(origin_data, data_type)
		if failed_data == '':
			array_data = []
			if is_version_control_req(data_type):
				array_data = self.get_version_ctr_array_result(origin_data, data_type)
			else:
				array_data = self.get_task_rpc_array_result(origin_data)
			# print 'array_data: '
			# print array_data

			dict_data = self.get_rpc_dict_result(array_data, data_type)
			# dict_data = self.get_rpc_dict_result(data_type, array_data)

			return {'data': dict_data, 'type': data_type}
		else:
			return {'data': failed_data, 'type': 'Failed'}

	def get_rpc_failed_data(self, origin_data, data_type):
		tmpdata = origin_data.split('\n')
		failed_data = ''
		if tmpdata[1].find('verControl Usage:') != -1:
			failed_data = 'verControl Failed'

		# failed_data = tmpdata
		# if is_version_control_req(data_type):
		# 	for value in tmpdata:
		# 		if value.find('---') != -1:
		# 			failed_data = ''
		# 			break
		# else:
		# 	failed_data = ''
		return failed_data

	def get_version_ctr_array_result(self, origin_data, data_type):
		tmpdata = origin_data.split('\n')
		array_data = []
		if data_type.find('show')!= -1:
			tmpdata = tmpdata[len(tmpdata)-2].split('\t')
			array_data.append(tmpdata)
		else:
			array_data.append(tmpdata[1:])
		# print tmpdata
		# for value in tmpdata:
		# 	if value != '':
		# 		array_data.append(value)
		return array_data

	def get_task_rpc_array_result(self, origin_data):
		tmpdata = origin_data.split('\n')
		tmpdata = tmpdata[1:len(tmpdata)-1]
		index = 0
		str_head = '[info]xxx: '
		info_flag = ': '
		other_flag = '::'

		final_result = []
		while index < len(tmpdata):
			tmp_result = []
			if tmpdata[index].find(info_flag) >= 0:
				# print tmpdata[index].find(info_flag)
				tmpdata[index] = tmpdata[index][tmpdata[index].find(info_flag) + len(info_flag):]
				tmpdata[index] = tmpdata[index].split(' ')
			elif tmpdata[index].find(other_flag) >= 0:
				# print tmpdata[index].find(other_flag)
				tmpdata[index] = tmpdata[index][tmpdata[index].find(other_flag) + len(other_flag):]
				tmpdata[index] = tmpdata[index].split(other_flag)
			# print tmpdata[index]
			for value in tmpdata[index]:
				if value != '':
					tmp_result.append(value)
			final_result.append(tmp_result)
			index += 1
		return final_result

	def get_rpc_dict_result(self, array_data, data_type):
		index = 0
		dict_data = []
		while index < len(array_data):
			tmp_dict_data = RpcResult(data_type, array_data[index])
			dict_data.append(tmp_dict_data.__dict__)
			index += 1
		return dict_data

class GetHtmlObject(object):
	def __init__(self):
		self.name = 'GetHtmlObject'

	def get_test_req_object(self):
		user = {
			'name': 'Python'
		}
		users = ['lee', 'Tom', 'Trump', 'Clinton']
		req_object = {
			'name': 'Django',
			'user': user,
			'users': users
		}
		return req_object

	def get_login_object(self):
		req_object = {
			'ENV_KEY': g_env_array
		}
		return req_object

	def get_admin_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_logout_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_password_change_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_group_object(self, id =''):
		group_array = []
		if id =='':
			group_obj = GroupInfo.objects.all()
			for tmp_obj in group_obj:
				group_array.append(Group(tmp_obj.name, tmp_obj.permission).__dict__)
		else:
			group_obj = GroupInfo.objects.get(name = id)
			if group_obj:
				group_array.append(Group(group_obj.name, group_obj.permission).__dict__)

		tmp_object = {
			'user': g_login_user,
			'groups': group_array,
			'group_numbs': len(group_array),
			'search_groupname': id
		}
		return tmp_object

	def get_admin_auth_group_add_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_group_change_object(self, cur_id = -1):
		group_json = {}
		if cur_id !=-1:
			group = GroupInfo.objects.filter(id = int(cur_id))[0]
			permission_array = []
			if group.permission == 'all':
				permission_array = g_group_permission
			elif group.permission != None:
				permission_array = group.permission.split(';')
				permission_array.remove('')

			group_json = {
				'name': group.name
			}
		tmp_object = {
			'login_user': g_login_user,
			'available_permissions': g_group_permission,
			'group': group_json,
			'permission': permission_array
		}
		return tmp_object

	def get_admin_auth_user_object(self, id=''):
		user_array = []
		if id == '':
			user_obj = UserInfo.objects.all()
			for tmp_obj in user_obj:
				user_array.append(User(tmp_obj.name, tmp_obj.email, \
				                  tmp_obj.permission, tmp_obj.groups).__dict__)
		else:
			user_obj = UserInfo.objects.get(name = id)
			if user_obj:
				user_array.append(User(user_obj.name, user_obj.email, \
				                  user_obj.permission, user_obj.groups, user_obj.password).__dict__)
		tmp_object = {
			'user': g_login_user,
			'users': user_array,
			'user_numb': len(user_array),
			'search_username': id
		}
		return tmp_object

	def get_admin_auth_user_add_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_user_change_object(self, cur_id = -1):
		user_json = {}
		if cur_id !=-1:
			user = UserInfo.objects.filter(id = int(cur_id))[0]
			permission_array = []
			user_groups = []
			available_groups = []
			group_obj = GroupInfo.objects.all()

			for tmp_obj in group_obj:
				available_groups.append(Group(tmp_obj.name, tmp_obj.permission).name)
			print type(user.permission)
			print user.permission
			if user.permission == 'all':
				permission_array = g_group_permission
			elif user.permission != None:
				permission_array = user.permission.split(';')
				permission_array.remove('')

			if user.groups == 'all':
				user_groups = available_groups
			elif user.groups != None :
				user_groups = user.groups.split(';')
				user_groups.remove('')

			user_json = {
				'name': user.name,
				'email': user.email
			}
		tmp_object = {
			'login_user': g_login_user,
			'user': user_json,
			'available_permissions': g_user_permission,
			'permission': permission_array,
			'available_groups': available_groups,
			'user_groups': user_groups
		}
		return tmp_object

server_view = ViewMain()

# def timer_start():
# 	t = threading.Timer(3, test_func, ("Timer_Start", ))
# 	t.start()
#
# def test_func(msg1):
# 	print ("I'm test_func, ", msg1)
# 	rsp_data = {'data': 'This is Timer'}
# 	response = HttpResponse(json.dumps(rsp_data))
# 	response["Access-Control-Allow-Origin"] = "*"
# 	response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 	response["Access-Control-Max-Age"] = "1000"
# 	response["Access-Control-Allow-Headers"] = "*"
# 	return response
# 	# timer_start()
