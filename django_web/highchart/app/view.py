from django.http import HttpResponse, Http404
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
import json

def index (request) :
	templateName = 'index.html'
	return render(request, templateName)

def get_jquery (request):
	return render(request, 'src/jquery-1.8.3/jquery.min.js')

def get_highchart (request):
	return render(request, "src/Highcharts-4.2.6/js/highcharts.js")

def get_highstock (request):
	return render(request, "src/Highstock-4.2.6/js/highstock.js")

def get_highchart_data (request):
	return render(request, "src/Highcharts-4.2.6/js/data.js")

def get_highchart_drilldown (request):
	return render(request, "src/Highcharts-4.2.6/js/drilldown.js")

def get_chart (request):
	return render(request, "chart.js")

@csrf_exempt
def sendData (request):
	data = {'A':[1,2,3], 'B':'BB'}
	return HttpResponse(json.dumps(data), content_type= "application/json")	

def ajax_dict (request):
	name_dict = {'twz': 'Life is short!'}
	return HttpResponse(json.dumps(name_dict), content_type = "application/json")