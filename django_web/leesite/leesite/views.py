from django.http import HttpResponse, Http404
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.shortcuts import render

import datetime

def hello (request):
	return HttpResponse("Hello LeeSite!")

def current_datetime_origin (request):
	now = datetime.datetime.now()
	html = "<html><body>It is now %s.</body></html>" % now
	return HttpResponse(html)

def current_datetime_step1 (request):
	now = datetime.datetime.now()
	t = Template("<html><body>It is now {{datetime}}.</body></html>")
	c = Context({'datetime': now})
	html = t.render(c)
	return HttpResponse(html)

def current_datetime_step2 (request):
	now = datetime.datetime.now()
	t = get_template("current_datetime.html")
	c = Context({'datetime': now})
	html = t.render(c)
	return HttpResponse(html)

def current_datetime (request):
	now = datetime.datetime.now()
	resContent = Context({'datetime': now})
	return render_to_response('current_datetime.html', resContent)

def hours_head (request, offset):
	try:
		offset = int(offset)
	except ValueError:
		raise Http404()
	dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
	html = "<html><body>In %s hours(s), it will be %s. </body></html>" % (offset, dt)
	return HttpResponse(html)

def index(request):
    return render(request, 'testScript.html')

def testScript(request):
	t = get_template("js/testScript.js")
	c = Context({'value': 'Come on'})
	jscript = t.render(c)
	return HttpResponse(jscript)

def add(request):
    a = request.GET['a']
    b = request.GET['b']
    a = int(a)
    b = int(b)
    return HttpResponse(str(a+b))


import json

def ajax_list(request):
    a = range(100)
    return HttpResponse(json.dumps(a), content_type='application/json')

def ajax_dict(request):
    name_dict = {'twz': 'Love python and Django', 'zqxt': 'I am teaching Django'}
    return HttpResponse(json.dumps(name_dict), content_type='application/json')	