# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GetData.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!
import sys
import threading
import time
from PyQt4 import QtCore, QtGui
from xml.dom import minidom 
import urllib2
import xml
import pyodbc
import datetime
import ConfigParser

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
    
#线程类
class GetDataThread(threading.Thread): #The timer class is derived from the class threading.Thread  
    def __init__(self, addr, port, username, userpwd, daname, project_id, component_id, interval, dbaddr, listWidget):  
        threading.Thread.__init__(self)  
        self.interval = interval  
        self.thread_stop = False
        self.addr = addr
        self.port = port
        self.username = username
        self.userpwd = userpwd
        self.daname = daname
        self.project_id = project_id
        self.component_id = component_id
        self.listWidget = listWidget
        self.dbaddr = dbaddr
    
    def ACI(self, url):
        response=urllib2.urlopen(url).read()
        return response

    def Change_Time(self, str_old):
        Months = {'Jan': '01', 'Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
        str_1 = str_old[5:8]
        str_new = str_old.replace(str_1,Months[str_1])
        return str_new
    
    def get_attrvalue(self, node, attrname):
        return node.getAttribute(attrname) if node else ''
    
    def get_nodevalue(self, node, index = 0):
        return node.childNodes[index].nodeValue if node else ''
    
    def get_xmlnode(self, node,name):
        return node.getElementsByTagName(name) if node else []
    

    def get_xml_data(self, root):
        
        actions_nodes = self.get_xmlnode(root,'actions')
        action_list=[]
        for actions_node in actions_nodes: 
            action_nodes = self.get_xmlnode(actions_node, "action")
            for node in action_nodes:
    
                node_token = self.get_xmlnode(node,'token')
                node_fetchaction = self.get_xmlnode(node,'fetchaction')
                node_status = self.get_xmlnode(node,'status')
                node_process_start_time = self.get_xmlnode(node,'process_start_time')
                node_process_end_time = self.get_xmlnode(node,'process_end_time')
                node_time_processing = self.get_xmlnode(node,'time_processing')
                node_queued_time = self.get_xmlnode(node,'queued_time')
                node_time_in_queue = self.get_xmlnode(node,'time_in_queue')
                
                if node_token :
                    action_token = self.get_nodevalue(node_token[0]).encode('utf-8','ignore')
                else :
                    action_token = ""
                if node_fetchaction :
                    action_fetchaction = self.get_nodevalue(node_fetchaction[0]).encode('utf-8','ignore')
                else :
                    action_fetchaction = ""
                if node_status :
                    action_status = self.get_nodevalue(node_status[0]).encode('utf-8','ignore')
                else :
                    action_status = ""
                if node_process_start_time :
                    action_process_start_time = self.get_nodevalue(node_process_start_time[0]).encode('utf-8','ignore')
                    action_process_start_time = self.Change_Time(action_process_start_time)
            
                else :
                    action_process_start_time = ""
                if node_process_end_time :
                    action_process_end_time = self.get_nodevalue(node_process_end_time[0]).encode('utf-8','ignore')
                    action_process_end_time = self.Change_Time(action_process_end_time)
    
                else :
                    action_process_end_time = ""
                if node_time_processing :
                    action_time_processing = self.get_nodevalue(node_time_processing[0]).encode('utf-8','ignore')
                else :
                    action_time_processing = ""
                if node_queued_time :
                    action_queued_time = self.get_nodevalue(node_queued_time[0]).encode('utf-8','ignore')
                    action_queued_time = self.Change_Time(action_queued_time)
    
                else :
                    action_queued_time = ""
                if node_time_in_queue :
                    action_time_in_queue = self.get_nodevalue(node_time_in_queue[0]).encode('utf-8','ignore')
                else :
                    action_time_in_queue = ""
                    
                    
                action = {}
                action['token'],action['fetchaction'],action['status'],action['process_start_time'],action['process_end_time'],action['time_processing'],action['queued_time'],action['time_in_queue'] = (
                    action_token, action_fetchaction, action_status,action_process_start_time, action_process_end_time,action_time_processing, action_queued_time, action_time_in_queue)
        
                action_list.append(action)
    
        return action_list
    
    
    def get_attr_value(self, root):
        
        #root = doc.documentElement
    
        actions_nodes = self.get_xmlnode(root,'actions')
        task_list=[]
        for actions_node in actions_nodes: 
            action_nodes = self.get_xmlnode(actions_node, "action")
            
            for node in action_nodes:
                
                node_token = self.get_xmlnode(node,'token')
                node_status = self.get_xmlnode(node,'status')
                node_docs = self.get_xmlnode(node,'documentcount')
                            
                if node_token :
                    action_token = self.get_nodevalue(node_token[0]).encode('utf-8','ignore')
                else :
                    action_token = ""
                    
                if node_status :
                    action_status = self.get_nodevalue(node_status[0]).encode('utf-8','ignore')
                else :
                    action_status = ""
                    
                for node in node_docs:
                    doc_task = self.get_attrvalue(node,'task')
                    doc_added = self.get_attrvalue(node,'added')
                    doc_updated = self.get_attrvalue(node,'updated')
                    doc_deleted = self.get_attrvalue(node,'deleted')
                    doc_ingestadded = self.get_attrvalue(node,'ingestadded')
                    doc_ingestupdated = self.get_attrvalue(node,'ingestupdated')
                    doc_ingestdeleted = self.get_attrvalue(node,'ingestdeleted')
                    doc_error = self.get_attrvalue(node,'errors')
                    
                    if doc_task:
                        task_name = self.get_attrvalue(node,'task')
                    else:
                        task_name =""
                    if doc_added:
                        task_added =  self.get_attrvalue(node,'added')
                    else:
                        task_added = 0
                    if doc_updated:
                        task_updated = self.get_attrvalue(node,'updated')
                    else :
                        task_updated = 0
                    if doc_deleted:
                        task_deleted = self.get_attrvalue(node,'deleted')
                    else:
                        task_deleted = 0
                    if doc_ingestadded:
                        task_ingestadded = self.get_attrvalue(node,'ingestadded')
                    else:
                        task_ingestadded = 0
                    if doc_ingestupdated:
                        task_ingestupdated = self.get_attrvalue(node,'ingestupdated')
                    else:
                        task_ingestupdated = 0                  
                    if doc_ingestdeleted:
                        task_ingestdeleted = self.get_attrvalue(node,'ingestdeleted')
                    else:
                        task_ingestdeleted = 0
                    if doc_error:
                        task_error = self.get_attrvalue(node,'errors')
                    else:
                        task_error = 0
                        
                    task = {}
                    task['action_token'],task['action_status'],task['task_name'],task['task_added'],task['task_updated'],task['task_deleted'],task['task_ingestadded'],task['task_ingestupdated'],task['task_ingestdeleted'],task['task_error'] = (
                    action_token,action_status,task_name,task_added,task_updated,task_deleted,task_ingestadded,task_ingestupdated,task_ingestdeleted,task_error)
    
                                        
                    task_list.append(task)
    
        return task_list
    
    def sql_execute(self, root, cursor, cnxn):
        action_list = self.get_xml_data(root)
        for action in action_list :
    
            if action['status'] == 'Processing' and action['fetchaction'] == 'SYNCHRONIZE':
                sql = "EXEC dbo.SP_AddAction \'%s\',\'%s\'" % (action['token'], self.component_id)
                
                self.listWidget.addItem(_fromUtf8("执行语句:" + sql))
                cursor.execute(sql)
                cnxn.commit()
                
            elif action['status'] == 'Finished' and action['fetchaction'] == 'SYNCHRONIZE':
                #sql = "EXEC dbo.SP_UpdateAction \'" + action['token'] + "\' , \'" + self.component_id + "\' , \'" + action['fetchaction'] + "\' , \'" +action['status'] + "\' , \'" + action['process_start_time']+ "\' , \'"+ action['process_end_time'] + "\' , \'" + action['time_processing'] + "\' , \'" + action['queued_time'] + "\' , \'" + action['time_in_queue'] + "\'"
                sql = "EXEC dbo.SP_UpdateAction \'%s\' , \'%s\' , \'%s\' , \'%s\' , \'%s\' , \'%s\' , \'%s\' , \'%s\' , \'%s\'" % (action['token'], self.component_id, action['fetchaction'],action['status'],action['process_start_time'],action['process_end_time'],action['time_processing'],action['queued_time'],action['time_in_queue'])
                self.listWidget.addItem(_fromUtf8("执行语句:" + sql))
                cursor.execute(sql)    
                cnxn.commit()        
                
        task_list = self.get_attr_value(root)
        for task in task_list :
    
            if task['action_status'] =='Processing':
                sql = "EXEC dbo.SP_AddTask \'%s\',\'%s\'" % (task['action_token'],task['task_name'])
                
                self.listWidget.addItem(_fromUtf8("执行语句:" + sql))
                cursor.execute(sql)
                cnxn.commit()
            elif task['action_status'] =='Finished':
                sql = "EXEC dbo.SP_UpdateTask \'%s\',\'%s\',%d,%d,%d,%d,%d,%d,%d" % (task['action_token'],task['task_name'],int(task['task_added']),int(task['task_updated']),int(task['task_deleted']),int(task['task_ingestadded']),int(task['task_ingestupdated']),int(task['task_ingestdeleted']),int(task['task_error']))
                
                self.listWidget.addItem(_fromUtf8("执行语句:" + sql))
                cursor.execute(sql)
                cnxn.commit()
    
    def run(self): #Overwrite run() method, put what you want the thread do here

        #C0043049.itcs.hp.com GVMetrics
        sqlconnect = "DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s" % (self.dbaddr, self.daname, self.username, self.userpwd)
        cnxn = pyodbc.connect(sqlconnect)
        cursor = cnxn.cursor()

        #actionUrl = 'http://16.178.110.201:16000/a=Queueinfo&queueaction=getstatus&queuename=fetch'
        actionUrl = "http://%s:%d/a=Queueinfo&queueaction=getstatus&queuename=fetch" % (self.addr, self.port)
        doc = minidom.parseString(self.ACI(actionUrl))
        root = doc.documentElement
    
        self.listWidget.addItem(_fromUtf8("开始查询:" + actionUrl))
        
        self.sql_execute(root,cursor, cnxn)
            
        while not self.thread_stop:
            sql = "EXEC dbo.SP_GetActionToken \'%s\'" % (self.component_id)
            cursor.execute(sql)
            #print tokens
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    #Tokens.append(row.action_token)
                    token_actionUrl = "http://%s:%d/a=Queueinfo&queueaction=getstatus&queuename=fetch&Token=%s" % (self.addr, self.port, row.action_token)
                    token_doc = minidom.parseString(self.ACI(token_actionUrl))
                    token_root = token_doc.documentElement
                    
                    self.listWidget.addItem(_fromUtf8("开始查询:" + token_actionUrl))
                    self.sql_execute(token_root, cursor, cnxn)
                #暂停10
                time.sleep(self.interval)
            else:
                break
            cursor.close()       
            cnxn.close()  
            self.listWidget.addItem(_fromUtf8("线程服务已运行结束"))
    def stop(self):  
        self.thread_stop = True

#窗口类
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(594, 550)
        
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 30, 570, 281))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(30, 40, 111, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.lineEditAddr = QtGui.QLineEdit(self.groupBox)
        self.lineEditAddr.setGeometry(QtCore.QRect(160, 40, 113, 20))
        self.lineEditAddr.setObjectName(_fromUtf8("lineEditAddr"))
        self.lineEditPort = QtGui.QLineEdit(self.groupBox)
        self.lineEditPort.setGeometry(QtCore.QRect(160, 100, 113, 20))
        self.lineEditPort.setObjectName(_fromUtf8("lineEditPort"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(30, 100, 111, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.lineEditDataBase = QtGui.QLineEdit(self.groupBox)
        self.lineEditDataBase.setGeometry(QtCore.QRect(160, 160, 113, 20))
        self.lineEditDataBase.setObjectName(_fromUtf8("lineEditDataBase"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(30, 160, 111, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.lineEditDataName = QtGui.QLineEdit(self.groupBox)
        self.lineEditDataName.setGeometry(QtCore.QRect(160, 210, 113, 20))
        self.lineEditDataName.setObjectName(_fromUtf8("lineEditDataName"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(30, 210, 111, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.lineEditPrjID = QtGui.QLineEdit(self.groupBox)
        self.lineEditPrjID.setGeometry(QtCore.QRect(420, 40, 113, 20))
        self.lineEditPrjID.setObjectName(_fromUtf8("lineEditPrjID"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(290, 40, 111, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.lineEditCmpID = QtGui.QLineEdit(self.groupBox)
        self.lineEditCmpID.setGeometry(QtCore.QRect(420, 100, 113, 20))
        self.lineEditCmpID.setObjectName(_fromUtf8("lineEditCmpID"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(290, 100, 111, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.lineEditUser = QtGui.QLineEdit(self.groupBox)
        self.lineEditUser.setGeometry(QtCore.QRect(420, 160, 113, 20))
        self.lineEditUser.setObjectName(_fromUtf8("lineEditUser"))
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(290, 160, 111, 16))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.lineEditPwd = QtGui.QLineEdit(self.groupBox)
        self.lineEditPwd.setGeometry(QtCore.QRect(420, 210, 113, 20))
        self.lineEditPwd.setObjectName(_fromUtf8("lineEditPwd"))
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setGeometry(QtCore.QRect(290, 210, 111, 16))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        
        self.lineEditTime = QtGui.QLineEdit(self.groupBox)
        self.lineEditTime.setGeometry(QtCore.QRect(420, 250, 113, 20))
        self.lineEditTime.setObjectName(_fromUtf8("lineEditTime"))
        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setGeometry(QtCore.QRect(290, 250, 111, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        
        self.pushButtonSave = QtGui.QPushButton(Dialog)
        self.pushButtonSave.setGeometry(QtCore.QRect(20, 325, 75, 23))
        self.pushButtonSave.setObjectName(_fromUtf8("pushButton"))
        
        self.pushButtonLoad = QtGui.QPushButton(Dialog)
        self.pushButtonLoad.setGeometry(QtCore.QRect(20, 350, 75, 23))
        self.pushButtonLoad.setObjectName(_fromUtf8("pushButton"))
        
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(20, 415, 75, 23))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        
        self.pushButtonStop = QtGui.QPushButton(Dialog)
        self.pushButtonStop.setGeometry(QtCore.QRect(20, 440, 75, 23))
        self.pushButtonStop.setObjectName(_fromUtf8("pushButton"))
        
        self.listWidget = QtGui.QListWidget(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(120, 320, 470, 192))
        self.listWidget.setObjectName(_fromUtf8("listWidget"))

        self.retranslateUi(Dialog)
        self.pushButton.clicked.connect(self.btn_exec)
        self.pushButtonSave.clicked.connect(self.btn_save)
        self.pushButtonLoad.clicked.connect(self.btn_load)
        self.pushButtonStop.clicked.connect(self.btn_stop)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        
        self.pushButtonLoad.setVisible(False)
        
        self.pushButtonStop.setEnabled(False)
                
        self.btn_load()

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "getdata", None))
        self.groupBox.setTitle(_translate("Dialog", "参数", None))
        self.label.setText(_translate("Dialog", "服务器地址", None))
        self.label_2.setText(_translate("Dialog", "服务器端口", None))
        self.label_3.setText(_translate("Dialog", "服务器用户", None))
        self.label_4.setText(_translate("Dialog", "服务器密码", None))
        self.label_5.setText(_translate("Dialog", "项目代码", None))
        self.label_6.setText(_translate("Dialog", "组件代码", None))
        self.label_7.setText(_translate("Dialog", "刷新时间", None))
        self.label_8.setText(_translate("Dialog", "数据库名", None))
        self.label_9.setText(_translate("Dialog", "数据库地址", None))
        self.pushButton.setText(_translate("Dialog", "执行", None))
        self.pushButtonSave.setText(_translate("Dialog", "保存参数", None))
        self.pushButtonLoad.setText(_translate("Dialog", "加载参数", None))
        self.pushButtonStop.setText(_translate("Dialog", "停止服务", None))
        
    def btn_exec(self):
        #project_id = 'SREP001'
        #component_id = 'SREP001_SPR001'
        addr = self.lineEditAddr.text()
        port = int(self.lineEditPort.text())
        username = self.lineEditUser.text()
        userpwd = self.lineEditPwd.text()
        daname = self.lineEditDataName.text()
        prgid = self.lineEditPrjID.text()
        compid = self.lineEditCmpID.text()
        interval = int(self.lineEditTime.text())
        dbaddr = self.lineEditDataBase.text()
        
        self.thread_ = GetDataThread(addr, port, username, userpwd, daname, prgid, compid,interval, dbaddr, self.listWidget) 
        self.thread_.start()
        
        self.listWidget.addItem(_fromUtf8("已启动数据服务")) 
        self.pushButton.setEnabled(False)
        self.pushButtonStop.setEnabled(True)
        
    def btn_save(self):
        config = ConfigParser.ConfigParser()
        config.add_section("parse")
        config.set("parse", "addr", self.lineEditAddr.text())
        config.set("parse", "port", self.lineEditPort.text())
        config.set("parse", "username", self.lineEditUser.text())
        config.set("parse", "userpwd", self.lineEditPwd.text())
        config.set("parse", "daname", self.lineEditDataName.text())
        config.set("parse", "prgid", self.lineEditPrjID.text())
        config.set("parse", "compid", self.lineEditCmpID.text())
        config.set("parse", "interval", self.lineEditTime.text())
        config.set("parse", "dbaddr", self.lineEditDataBase.text())
        
        config.write(open("parse.ini","w"))
        
        self.btn_load()
    
    def btn_load(self):
        try:
            config = ConfigParser.ConfigParser()
            config.readfp(open("parse.ini"))
            self.lineEditAddr.setText(config.get("parse", "addr"))
            self.lineEditPort.setText(config.get("parse", "port"))
            self.lineEditUser.setText(config.get("parse", "username"))
            self.lineEditPwd.setText(config.get("parse", "userpwd"))
            self.lineEditDataName.setText(config.get("parse", "daname"))
            self.lineEditPrjID.setText(config.get("parse", "prgid"))
            self.lineEditCmpID.setText(config.get("parse", "compid"))
            self.lineEditTime.setText(config.get("parse", "interval"))
            self.lineEditDataBase.setText(config.get("parse", "dbaddr"))
        except:
            return
        
    def btn_stop(self):
        self.thread_.stop()
        self.thread_.join()
        self.listWidget.addItem(_fromUtf8("数据服务已停止"))
        self.pushButton.setEnabled(True)
        self.pushButtonStop.setEnabled(False)
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    da = Ui_Dialog()
    qw = QtGui.QDialog()
    da.setupUi(qw)
    qw.show()
    sys.exit(app.exec_())
    