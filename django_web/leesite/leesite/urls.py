"""leesite URL Configuration

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
urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

"""
from django.conf.urls import url
from django.contrib import admin
from leesite.views import hello, current_datetime, hours_head
from leesite.views import index, add, ajax_dict, ajax_list, testScript

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^hello/$', hello),
    url(r'^time/$', current_datetime),
    url(r'^time/plus/(\d{1,2})/$', hours_head),
    url(r'^$', index),
    url(r'^add/$', add),
    url(r'^ajax_dict',ajax_dict),
    url(r'^ajax_list', ajax_list),
    url(r'^testScript.js/$',testScript),
]
