# -*- coding: UTF-8 -*-

import os,sys

#del os.environ["TMPPYTHONPATH"]
work_path = os.getenv('TMPPYTHONPATH')
# print 'work_path: %s'%(work_path)
# print 'os.getcwd(): %s'%(os.getcwd())

if work_path is None:
    #pyd安装文件所在的路径
    print os.getcwd();
    # work_path = r"C:\QtAPI\python";
    work_path = r"E:\github\study\python work"
sys.path.append(work_path)
import QtPyAPI

os.chdir(os.getcwd())
# print "QtAPI, Current Work Dir: %s" % (os.getcwd())


#********* QtAPI登录，启动API环境 *************
#param qtUser Qt用户
#param qtPwd Qt用户密码
#param option 预留参数，逗号分割的键值对序列
#ret 0 成功 >0 错误
def QtLogin(qtUser,qtPwd,options = ""):
    strLogin = QtPyAPI.string()
    ret = QtPyAPI.QtLogin(strLogin, qtUser, qtPwd, options)
    return ret, strLogin.c_str()
    
#************ QtAPI登出，停止API环境  *************
#note  QtAPI登出必须使用原QtAPI登录用户进行。
#param gtaUsr 国泰安用户
#ret 0 成功  >0 错误 
def QtLogout(qtUser):
    errorMsg = QtPyAPI.string()
    ret = QtPyAPI.QtLogout(errorMsg, qtUser)
    return ret, errorMsg.c_str()

if __name__=='__main__':
    pass


