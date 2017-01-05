import re

def test_req():
	str = "http://127.0.0.1:8000/chart.js"

	# str = "chart.js"
	reg_str = 'chart.js'
	if re.match(reg_str, str):
		print 'Perfect match'
	else:
		print 'Failed'

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

def test_get_ajax_request_name():
	path = '/a/AJAX/b/c/'
	print 'original file name: ' + path
	print 'transed file name:  ' + get_ajax_request_name(path)

def test_get_file_name():
	path = '/a/b/c.html/'
	print 'original file name: ' + path
	print 'transed file name:  ' + get_file_name(path)

def test_get_static_file_name():
	path = '/a/static/b/c.js/'
	print 'original file name: ' + path
	print 'transed file name:  ' + get_static_file_name(path)

def global_func():
	test_get_file_name()
	# test_get_static_file_name()
	# test_get_ajax_request_name()

global_func()


