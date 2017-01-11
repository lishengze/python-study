from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import auth
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect

import os
import sys
import socket
import datetime
import json

def query_all_srvstatus(request):
    rsp_data = {'data': 'query_all_srvstatus'}
    response = HttpResponse(json.dumps(rsp_data))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def query_all_tasklist(request):
    rsp_data = {'data': 'query_all_tasklist'}
    response = HttpResponse(json.dumps(rsp_data))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def query_all_taskresult(request):
    rsp_data = {'data': 'query_all_taskresult'}
    response = HttpResponse(json.dumps(rsp_data))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def query_all_version(request):
    rsp_data = {'data': 'query_all_version'}
    response = HttpResponse(json.dumps(rsp_data))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def default_ajax_request(request):
    	return HttpResponse(json.dumps({'data':'AJAX Request Failed!'}),
                            content_type = "application/json")

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

def is_empty_html_request(file_name):
	name_array = file_name.split('/')
	last_file_name = name_array[len(name_array)-1]
	if last_file_name.find('.') == -1:
		return True
	else:
		return False

def is_html_request(path_name):
	html_flag = '.html'
	flag = False
	if len(path_name) > len(html_flag) and path_name[-len(html_flag):] == html_flag:
		flag = True
	return flag

def get_file_name(path):
	file_name = delete_headend_slash(path)
	html_flag = '.html'
	if is_static_file(file_name):
		file_name = get_static_file_name(file_name)
	if is_empty_html_request(file_name):
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
		'Request_All_SrvStatus': query_all_srvstatus,
		'Request_All_TaskList': query_all_tasklist,
		'Request_All_TaskResult': query_all_taskresult,
		'Request_All_Version': query_all_version
	}
	ajax_func = ajax_func_dict.get(ajax_name, default_ajax_request)
	return ajax_func

def get_file_object(file_name):
	file_object_dict = {
		'main.html': get_main_object
	}
	object_func = file_object_dict.get(file_name, lambda :{})
	print object_func()
	return object_func()

def main_query_rsp(request):
	if is_ajax_request(request.path):
		print '\nIs AJAX Request'
		ajax_func = get_ajax_func(request.path)
		return ajax_func(request)
	else:
		print '\nIs not AJAX Request'
		file_name = get_file_name(request.path)
		file_object = {}
		if is_html_request(file_name):
			file_object = get_file_object(file_name)
		print 'file name: ' + file_name + '\n'
		return render(request, file_name, file_object)

def get_admin_auth_group_object():
	return {'name': 'Manager'}

def get_main_object():
	return {'name': 'LEE'}
