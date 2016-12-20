#!/usr/bin/python
#	-*-	coding:	utf-8	-*-

"""blog_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve
from blog import views as blog_views
from feed import LatestEntriesFeed

admin.autodiscover() 
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'root/(?P<path>.*)$', serve,
    {'document_root': 'C:\Users\chen.xiaohong\Desktop\django_web\blog_test\templates'}),
    url(r'^$',blog_views.index),
    url(r'^account/login/', blog_views.alogin),
    url(r'^account/register/', blog_views.register),
    url(r'^account/logout/', blog_views.alogout),
    url(r'^essay/(?P<eid>\d+)/',blog_views.essay_details),
    url(r'^search/',blog_views.search),
    url(r'^leavemsg/(?P<eid>\d+)/',blog_views.leave_comment1),
    url(r'^(?P<pageNo>\d+)/(?P<etype>\d+)/',blog_views.index),
    url(r'^latest/feed/', LatestEntriesFeed()),

]
