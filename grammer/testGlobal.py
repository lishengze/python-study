# -*- coding: utf-8 -*-

g_users = {} 
g_groups = {}
g_chosen_user = {} 
g_chosen_group = {}
g_login_user = {}

class User(object):
	def __init__(self, name = 'tmp', email = 'tmp', permisson = 'all'):
		self.name = name
		self.email = email
		self.permisson = permisson

	def __dict__(self):
		return {
			'name': self.name,
			'email': self.email,
			'permisson': self.permisson
		}

class Group(object):
	def __init__(self, name = 'tmp', permisson = 'all'):
		self.name = name
		self.permisson = permisson

	def __dict__(self):
		return {
			'name': self.name,
			'permisson': self.permisson
		}

def init_globals():
	global g_users, g_groups, g_login_user
	Trump = User('Trump', 'Trump@gmail.com')
	Clinton = User('Clinton', 'Clinton@gmail.com')
	Obama = User('Obama', 'Obama@gmail.com')
	g_users = [Trump, Clinton, Obama]

	communist_party = Group(u'共产党')
	democratic_party = Group(u'民主党')
	republican_party = Group(u'共和党')
	g_groups = [communist_party, democratic_party, republican_party]

	g_login_user = User('SHFE.SFIT', 'SHFE.SFIT@hotmail.com')

init_globals()

def testFunc():
	print g_users
	print g_groups
	print g_login_user

testFunc()