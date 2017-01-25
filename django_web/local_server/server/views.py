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
from django.views.decorators.csrf import csrf_protect, csrf_exempt

import json
from models import Person
from models import GroupInfo

g_users = {}
g_groups = {}
g_chosen_user = {}
g_chosen_group = {}
g_login_user = {}
g_env_array = []

class User(object):
	def __init__(self, name = 'tmp', email = 'tmp', permisson = 'all'):
		self.name = name
		self.email = email
		self.permisson = permisson
		self.__dict__ = {
			'name': self.name,
			'email': self.email,
			'permisson': self.permisson
		}

class Group(object):
	def __init__(self, name = 'tmp', permisson = 'all'):
		self.name = name
		self.permisson = permisson
		self.__dict__ = {
			'name': self.name,
			'permisson': self.permisson
		}

def init_globals():
	global g_users, g_groups, g_login_user, g_chosen_user, g_chosen_group, g_env_array
	Trump = User('Trump', 'Trump@gmail.com')
	Clinton = User('Clinton', 'Clinton@gmail.com')
	Obama = User('Obama', 'Obama@gmail.com')
	Bush = User('Bush', 'Bush@gmail.com')
	g_users = [Trump, Clinton, Obama, Bush]
	g_chosen_user = Trump

	# communist_party = Group('Communist Party')
	# democratic_party = Group('Democratic Party')
	# republican_party = Group('Republican Party')

	communist_party = Group('共产党')
	democratic_party = Group('民主党')
	republican_party = Group('共和党')
	g_groups = [communist_party, democratic_party, republican_party]
	g_chosen_group = republican_party

	g_login_user = User('SHFE.SFIT', 'SHFE.SFIT@hotmail.com')
	g_env_array = ['TEST_170', 'PTEST_170']

init_globals()

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

	def is_static_file(self, file_name):
		name_array = file_name.split('/')
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

	def get_static_file_name(self, origin_file_name):
		name_array = origin_file_name.split('/')
		index = 0
		static_flag = 'static'
		for value in name_array:
			if value == static_flag:
				break
			index += 1
		trans_file_name = '/'.join(name_array[index:])
		return self.delete_headend_slash(trans_file_name)

	def get_html_file_name(self, path):
		name_array = path.split('/')
		return name_array[len(name_array)-1]

	def is_empty_html_request(self, file_name):
		name_array = file_name.split('/')
		last_file_name = name_array[len(name_array)-1]
		if last_file_name.find('.') == -1:
			return True
		else:
			return False

	def is_html_request(self, path_name):
		html_flag = '.html'
		flag = False
		if len(path_name) > len(html_flag) and path_name[-len(html_flag):] == html_flag:
			flag = True
		return flag

	def get_file_name(self, path):
		file_name = self.delete_headend_slash(path)
		html_flag = '.html'
		# if is_static_file(file_name):
		# 	file_name = get_static_file_name(file_name)
		if self.is_empty_html_request(file_name):
			file_name += html_flag
		return file_name

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
			'Set_Chosen_GroupOrUser': self._ajax_func.set_chosen_grouporuser,
			'Upload_File': self._ajax_func.upload_file,
			'Set_DB_Data': self._ajax_func.set_dbdata,
			'Get_DB_Data': self._ajax_func.get_dbdata,
			'Delete_Group': self._ajax_func.delete_group_data,
			'Add_Group': self._ajax_func.add_group_data,
		}
		ajax_func = ajax_func_dict.get(ajax_name, self._ajax_func.default_ajax_request)
		return ajax_func

	def get_file_object(self, file_name):
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
		object_func = file_object_dict.get(file_name, lambda :{})
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
			file_name = self.get_file_name(request.path)
			file_object = {}
			if self.is_html_request(file_name):
				file_object = self.get_file_object(file_name)
			print 'file name: ' + file_name + '\n'
			return render(request, file_name, file_object)

class AjaxReqFunc(object):
	def __init__ (self):
		self.name = 'AjaxReqFunc'

	def default_ajax_request(self, request):
		return HttpResponse(json.dumps({'data':'AJAX Request Failed!'}), content_type = "application/json")

	def set_dbdata(self, request):
		# tmp_data = Person(name='LSZ', age=27)
		# tmp_data.save()

		for group_data in g_groups:
			db_obj = GroupInfo(name = group_data.name, permission = group_data.permisson)
			db_obj.save()

		rsp_data = {'data': 'set database data!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def get_dbdata(self, request):
		person_obj = Person.objects.all()
		result = {
			'name': person_obj[0].name,
			'age': person_obj[0].age
		}

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
		delete_data = request.POST.getlist('delete_group')
		successful_delete_data = []
		failed_delete_data = []
		for value in delete_data:
			if GroupInfo.objects.filter(name = value).delete():
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
		add_data = request.POST.getlist('req_data')
		add_group = GroupInfo(name = add_data.name, permission = add_data.permission)
		status = 'Failed'
		if add_group.save() :
			status = 'Successful'

		rsp_data = {'status': status}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response			

	def upload_file(self, request):
		rsp_data = {}
		if request.method == 'POST':
			start_time = int(time.time())
			upload_file = request.FILES['file']
			if upload_file:
				filename = str(upload_file).encode('utf-8')

				self.handle_uploaded_file(upload_file, filename)

				# filepath = os.path.join(cfg.WORK_PATH_TEMP, filename)
				# filedst = filepath + cfg.DOT + cfg.PID
				# destination = open(filepath,'wb+')
				# for chunk in upload_file.chunks():
				# 	destination.write(chunk)
				# destination.close()
				# status = 'Successful'
				# sock = sock_conn(ENV_KEY)
				# rtn = uploadFile(sock, filepath, filedst)
				# end_time = int(time.time())
				# upload_time = str(end_time - start_time)
				# print 'rtn: ', rtn
				# if rtn == cfg.CMD_SUCC:
				# 	rsp = recv_end(sock)
				# 	info = '<br/>File transfer SUCC, cost ' + str(end_time - start_time) + ' secs.'
				# 	status = "Successful"
				# else:
				# 	info = '<br/>File transfer FAIL, cost ' + str(end_time - start_time) + ' secs.'
				# 	status = 'Failed'
				# rsp = rsp + info
				# print rsp
				# print 'status: ', status
				# sock.close()

				rsp_data = {
					'type': 'Successful',
					'upload_time': 1
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
		full_file_name = 'upload/' + filename
		with open(full_file_name, 'wb+') as destination:
			for chunk in file.chunks():
				destination.write(chunk)
		destination.close()

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

	@csrf_exempt
	def test_task_rpc(self, request):
		rsp_data = {'data': 'test_task_rpc!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def test_task_ntf(self, request):
		rsp_data = {'data': 'test_task_ntf!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def test_all_srvstatus(self, request):
		rsp_data = {'data': 'test_all_srvstatus!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def test_all_tasklist(self, request):
		rsp_data = {'data': 'test_all_tasklist!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def test_all_taskresult(self, request):
		rsp_data = {'data': 'test_all_taskresult!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def test_all_version(self, request):
		rsp_data = {'data': 'test_all_version!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def set_chosen_grouporuser(self, request):
		global g_users, g_groups, g_chosen_user, g_chosen_group
		test_value = request.POST.getlist('test_value')[0]
		# print test_value
		test_value = test_value.encode('utf-8')
		print test_value
		rsp_url = ''
		error_info = ''

		is_user_request = False
		is_group_request = False
		for group in g_groups:
			if test_value == group.name:
				g_chosen_group = group
				is_group_request = True
		for user in g_users:
			if test_value == user.name:
				g_chosen_user = user
				is_user_request = True

		if is_group_request:
			rsp_url = '/admin/auth/group/change'
		elif is_user_request:
			rsp_url = '/admin/auth/user/change'
		else :
			error_info = 'request name does not exit!'

		rsp_data = {'data': rsp_url,
					'error': error_info}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

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

	def get_admin_auth_group_object(self):
		group_array = []
		group_obj = GroupInfo.objects.all()
		
		for tmp_obj in group_obj:
			group_array.append(Group(tmp_obj.name, tmp_obj.permission).__dict__)
		
		tmp_object = {
			'user': g_login_user,
			'groups': group_array,
			'group_numbs': len(group_array)
		}
		return tmp_object

	def get_admin_auth_group_add_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_group_change_object(self):
		tmp_object = {
			'login_user': g_login_user,
			'group': g_chosen_group
		}
		return tmp_object

	def get_admin_auth_user_object(self):
		tmp_object = {
			'user': g_login_user,
			'users': g_users,
			'user_numb': len(g_users)
		}
		return tmp_object

	def get_admin_auth_user_add_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_user_change_object(self):
		tmp_object = {
			'login_user': g_login_user,
			'chosen_user': g_chosen_user
		}
		return tmp_object

server_view = ViewMain()
