
class Func(object):
	def __init__(self):
		self.fa = funca
		self.fb = funcb

def listFunc():
	func_list = {
		'a': funca,
		'b': funcb
	}
	func = func_list.get('a')
	func()
	for value in func_list:
		print type(value)

	# tmpObj = Func()
	# tmpObj.fa()
	
	tmpFunc = funcb()
	tmpFunc()

def funca():
	print 'funca'

def funcb():
	print 'funcb'
	return funca


def global_func():
	listFunc()

global_func()
