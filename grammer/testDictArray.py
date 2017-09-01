# -*- coding: utf-8 -*-
g_users = {}
g_groups = {}
g_chosen_user = {}
g_chosen_group = {}
g_login_user = {}
g_users_test = {}

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

def init_globals():
	global g_users, g_groups, g_login_user, g_users_test
	Trump = User('Trump', 'Trump@gmail.com')
	Clinton = User('Clinton', 'Clinton@gmail.com')
	Obama = User('Obama', 'Obama@gmail.com')
	Bush = User('Bush', 'Bush@gmail.com')
	g_users_test[Trump.name] = Trump
	g_users_test[Clinton.name] = Clinton
	g_users_test[Obama.name] = Obama
	g_users_test[Bush.name] = Bush
	g_users = [Trump, Clinton, Obama, Bush]
	g_chosen_user = Trump

	communist_party = Group('共产党')
	democratic_party = Group('民主党')
	republican_party = Group('共和党')
	g_groups = [communist_party, democratic_party, republican_party]
	g_chosen_group = republican_party

	g_login_user = User('SHFE.SFIT', 'SHFE.SFIT@hotmail.com')

init_globals()

def testFunc():
	global g_users, g_users_test
	for value in g_users:
		print value.name
	for value in g_users_test:
		print value, g_users_test[value].email
	if 'Obama' in g_users_test:
		print 'True'
testFunc()