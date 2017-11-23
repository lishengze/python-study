# -*- coding: UTF-8 -*-
'''
Created on 2015年9月21日

@author: chenjuan
'''

from xml.dom import minidom 
import urllib2
import xml
import pyodbc
import datetime
import time

def ACI(url):
    response=urllib2.urlopen(url).read()
    return response

def Change_Time(str_old):
    Months = {'Jan': '01', 'Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    str_1 = str_old[5:8]
    str_new = str_old.replace(str_1,Months[str_1])
    return str_new

def get_attrvalue(node, attrname):
    return node.getAttribute(attrname) if node else ''

def get_nodevalue(node, index = 0):
    return node.childNodes[index].nodeValue if node else ''

def get_xmlnode(node,name):
    return node.getElementsByTagName(name) if node else []

project_id = 'SREP001'
component_id = 'SREP001_SPR001'


def get_xml_data(root):
    
    actions_nodes = get_xmlnode(root,'actions')
    action_list=[]
    for actions_node in actions_nodes: 
        action_nodes = get_xmlnode(actions_node, "action")
        for node in action_nodes:

            node_token = get_xmlnode(node,'token')
            node_fetchaction = get_xmlnode(node,'fetchaction')
            node_status = get_xmlnode(node,'status')
            node_process_start_time = get_xmlnode(node,'process_start_time')
            node_process_end_time = get_xmlnode(node,'process_end_time')
            node_time_processing = get_xmlnode(node,'time_processing')
            node_queued_time = get_xmlnode(node,'queued_time')
            node_time_in_queue = get_xmlnode(node,'time_in_queue')
            
            if node_token :
                action_token =get_nodevalue(node_token[0]).encode('utf-8','ignore')
            else :
                action_token = ""
            if node_fetchaction :
                action_fetchaction =get_nodevalue(node_fetchaction[0]).encode('utf-8','ignore')
            else :
                action_fetchaction = ""
            if node_status :
                action_status =get_nodevalue(node_status[0]).encode('utf-8','ignore')
            else :
                action_status = ""
            if node_process_start_time :
                action_process_start_time = get_nodevalue(node_process_start_time[0]).encode('utf-8','ignore')
                action_process_start_time = Change_Time(action_process_start_time)
        
            else :
                action_process_start_time = ""
            if node_process_end_time :
                action_process_end_time = get_nodevalue(node_process_end_time[0]).encode('utf-8','ignore')
                action_process_end_time = Change_Time(action_process_end_time)

            else :
                action_process_end_time = ""
            if node_time_processing :
                action_time_processing =get_nodevalue(node_time_processing[0]).encode('utf-8','ignore')
            else :
                action_time_processing = ""
            if node_queued_time :
                action_queued_time = get_nodevalue(node_queued_time[0]).encode('utf-8','ignore')
                action_queued_time = Change_Time(action_queued_time)

            else :
                action_queued_time = ""
            if node_time_in_queue :
                action_time_in_queue =get_nodevalue(node_time_in_queue[0]).encode('utf-8','ignore')
            else :
                action_time_in_queue = ""
                
                
            action = {}
            action['token'],action['fetchaction'],action['status'],action['process_start_time'],action['process_end_time'],action['time_processing'],action['queued_time'],action['time_in_queue'] = (
                action_token, action_fetchaction, action_status,action_process_start_time, action_process_end_time,action_time_processing, action_queued_time, action_time_in_queue)
    
            action_list.append(action)

    return action_list


def get_attr_value(root):
    
    #root = doc.documentElement

    actions_nodes = get_xmlnode(root,'actions')
    task_list=[]
    for actions_node in actions_nodes: 
        action_nodes = get_xmlnode(actions_node, "action")
        
        for node in action_nodes:
            
            node_token = get_xmlnode(node,'token')
            node_status = get_xmlnode(node,'status')
            node_docs = get_xmlnode(node,'documentcount')
                        
            if node_token :
                action_token =get_nodevalue(node_token[0]).encode('utf-8','ignore')
            else :
                action_token = ""
                
            if node_status :
                action_status =get_nodevalue(node_status[0]).encode('utf-8','ignore')
            else :
                action_status = ""
                
            for node in node_docs:
                doc_task = get_attrvalue(node,'task')
                doc_added = get_attrvalue(node,'added')
                doc_updated = get_attrvalue(node,'updated')
                doc_deleted = get_attrvalue(node,'deleted')
                doc_ingestadded = get_attrvalue(node,'ingestadded')
                doc_ingestupdated = get_attrvalue(node,'ingestupdated')
                doc_ingestdeleted = get_attrvalue(node,'ingestdeleted')
                doc_error = get_attrvalue(node,'errors')
                
                if doc_task:
                    task_name = get_attrvalue(node,'task')
                else:
                    task_name =""
                if doc_added:
                    task_added =  get_attrvalue(node,'added')
                else:
                    task_added = 0
                if doc_updated:
                    task_updated = get_attrvalue(node,'updated')
                else :
                    task_updated = 0
                if doc_deleted:
                    task_deleted = get_attrvalue(node,'deleted')
                else:
                    task_deleted = 0
                if doc_ingestadded:
                    task_ingestadded = get_attrvalue(node,'ingestadded')
                else:
                    task_ingestadded = 0
                if doc_ingestupdated:
                    task_ingestupdated = get_attrvalue(node,'ingestupdated')
                else:
                    task_ingestupdated = 0                  
                if doc_ingestdeleted:
                    task_ingestdeleted = get_attrvalue(node,'ingestdeleted')
                else:
                    task_ingestdeleted = 0
                if doc_error:
                    task_error = get_attrvalue(node,'errors')
                else:
                    task_error = 0
                    
                task = {}
                task['action_token'],task['action_status'],task['task_name'],task['task_added'],task['task_updated'],task['task_deleted'],task['task_ingestadded'],task['task_ingestupdated'],task['task_ingestdeleted'],task['task_error'] = (
                action_token,action_status,task_name,task_added,task_updated,task_deleted,task_ingestadded,task_ingestupdated,task_ingestdeleted,task_error)

                                    
                task_list.append(task)

    return task_list

def sql_execute(root):
    action_list = get_xml_data(root)
    for action in action_list :

        if action['status'] == 'Processing' and action['fetchaction'] == 'SYNCHRONIZE':
            sql = "EXEC dbo.SP_AddAction \'%s\',\'%s\'" % (action['token'],component_id)
            cursor.execute(sql)
            cnxn.commit()
            
        elif action['status'] == 'Finished' and action['fetchaction'] == 'SYNCHRONIZE':
            sql = "EXEC dbo.SP_UpdateAction \'" + action['token'] + "\' , \'" + component_id + "\' , \'" + action['fetchaction'] + "\' , \'" +action['status'] + "\' , \'" + action['process_start_time']+ "\' , \'"+ action['process_end_time'] + "\' , \'" + action['time_processing'] + "\' , \'" + action['queued_time'] + "\' , \'" + action['time_in_queue'] + "\'"
            cursor.execute(sql)    
            cnxn.commit()        
            
    task_list = get_attr_value(root)
    for task in task_list :

        if task['action_status'] =='Processing':
            sql = "EXEC dbo.SP_AddTask \'%s\',\'%s\'" % (task['action_token'],task['task_name'])
            cursor.execute(sql)
            cnxn.commit()
        elif task['action_status'] =='Finished':
            sql = "EXEC dbo.SP_UpdateTask \'%s\',\'%s\',%d,%d,%d,%d,%d,%d,%d" % (task['action_token'],task['task_name'],int(task['task_added']),int(task['task_updated']),int(task['task_deleted']),int(task['task_ingestadded']),int(task['task_ingestupdated']),int(task['task_ingestdeleted']),int(task['task_error']))
            print sql
            cursor.execute(sql)
            cnxn.commit()


if __name__ == "__main__":
    
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=C0043049.itcs.hp.com;DATABASE=GVMetrics;UID=sa;PWD=sa')
    cursor = cnxn.cursor()

    actionUrl = 'http://16.178.110.201:16000/a=Queueinfo&queueaction=getstatus&queuename=fetch'
    doc = minidom.parseString(ACI(actionUrl))
    root = doc.documentElement
    
    sql_execute(root)
            
    while True:
        sql = "EXEC dbo.SP_GetActionToken \'%s\'" % (component_id)
        cursor.execute(sql)
        #print tokens
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                #Tokens.append(row.action_token)
                 token_actionUrl = 'http://16.178.110.201:16000/a=Queueinfo&queueaction=getstatus&queuename=fetch&Token=%s' % row.action_token
                 token_doc = minidom.parseString(ACI(token_actionUrl))
                 token_root = token_doc.documentElement
                 sql_execute(token_root)
                 #暂停10
            time.sleep(10)
        else:
            break
    
    cursor.close()       
    cnxn.close()
              
            