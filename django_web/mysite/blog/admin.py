#coding=utf-8
'''
Created on 2010-12-26

@author: xugang
'''
from blog.models import Users, EssayType, Essay,Comment, LevelMsg, Archive
from django.contrib import admin
#��Admin��ע��һ������ģ��
admin.site.register(Users)
admin.site.register(EssayType)
admin.site.register(Essay)
admin.site.register(Comment)
admin.site.register(LevelMsg)
admin.site.register(Archive)