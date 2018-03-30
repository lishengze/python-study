# -*- coding: UTF-8 -*-
import sys
import pymssql  
from CONFIG import *
from toolFunc import *
import time

reload(sys)
sys.setdefaultencoding('utf-8')

class Database:
    def __init__(self, id=0, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        self.__name__ = "Database"
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.id = id
        self.insertDataNumbOnce = 1000
        self.startConnect()

    def __del__(self):
        self.closeConnect()

    def startConnect(self):
        self.conn = pymssql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, \
                                    timeout=5, login_timeout=2, charset="utf8")
        self.cur = self.conn.cursor()
        if not self.cur:
            raise(NameError, "Connect Data Base Failed! ")

    def closeConnect(self):
        self.conn.close()  

    def get_database_data(self,sql):  
        self.cur.execute(sql)  
        result = self.cur.fetchall()  
        return result  
  
    def changeDatabase(self,sql):  
        # try:
        #     result = self.cur.execute(sql)  
        #     result2 = self.conn.commit()  
        #     return result
        # except Exception as e:
        #     exception_info = "\n" + str(traceback.format_exc()) + '\n'
        #     duplicate_insert_error = "Violation of PRIMARY KEY constraint"
        #     if duplicate_insert_error not in exception_info:
        #         raise(Exception(exception_info))     
        result = self.cur.execute(sql)  
        result2 = self.conn.commit()  
        return result           

    def dropTableByName(self, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "drop table " + complete_tablename 
        self.changeDatabase(sql_str)

    def clearDatabase(self):
        table_info = self.getDatabaseTableInfo()
        for table_name in table_info: 
                self.dropTableByName(table_name)        

    def get_create_str(self,table_name):
        pass

    def get_insert_str(self,oridata, table_name):
        pass

    def filter_source(self, source):
        return source

    def filter_tableArray(self, tableArray):
        return tableArray

    def createTableByName(self, table_name):
        create_str = self.get_create_str(table_name)
        # print create_str
        self.changeDatabase(create_str)

    def completeDatabaseTable (self, tableNameArray):
        table_info = self.getDatabaseTableInfo()
        for table_name in tableNameArray:            
            if table_name not in table_info:
                self.createTableByName(table_name)

    def refreshDatabase(self, tableNameArray):
        table_info = self.getDatabaseTableInfo()
        for table_name in tableNameArray:
            if table_name in table_info:
                self.dropTableByName(table_name)
            self.createTableByName(table_name)    

    def insert_data(self, oridata, table_name):
        try:
            insert_str = self.get_insert_str(oridata, table_name)
            result = self.changeDatabase(insert_str)

            if result != None:
                print 'insert result: ', result
                print '\n^^^^^ database insert_data restart! ^^^^^ \n'
                time.sleep(connFailedWaitTime)
                self.insert_data(oridata, table_name)
            return result
        except Exception as e:
            connect_error = "20003"
            if connect_error in e[1]:
                connFailedWaitTime = 5
                print '\n^^^^^20003 connection timed out database insert_data restart! ^^^^^ \n'
                time.sleep(connFailedWaitTime)
                self.insert_data(oridata, table_name)        
            else:
                raise(e)

    def insert_multi_data(self, oridataArray, table_name):
        start_index = 0
        while start_index < len(oridataArray):
            end_index = start_index + self.insertDataNumbOnce
            if end_index > len(oridataArray):
                end_index = len(oridataArray)

            insert_str = self.get_multi_insert_str(oridataArray[start_index:end_index], table_name)
            self.changeDatabase(insert_str)
            
            start_index = end_index

    def get_datacount(self, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = 'select count(*) from ' + complete_tablename
        result = self.get_database_data(sql_str)
        return result[0][0]

    def getDatabaseTableInfo(self):
        queryString = "select name from "+ self.db +"..sysobjects where xtype= 'U'"
        result = self.get_database_data(queryString)
        transRst = []
        for i in range(len(result)):
            transRst.append(str(result[i][0]))
        return transRst    

    def getDataByTableName(self, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = 'select * from ' + complete_tablename
        result = self.get_database_data(sql_str)
        return result

    def getStartEndTime(self, oriStartTime, oriEndTime, tableDataStartTime, tableDataEndTime):
        timeArray = []
        if tableDataStartTime is None or tableDataEndTime is None:
            timeArray.append([oriStartTime, oriEndTime])
        else:
            # if oriEndTime > getIntegerDateNow():
            #     oriEndTime = getIntegerDateNow()

            # if tableDataEndTime > getIntegerDateNow():
            #     tableDataEndTime = getIntegerDateNow()

            if oriStartTime >=  tableDataStartTime and oriEndTime > tableDataEndTime:
                startTime = addOneDay(tableDataEndTime)
                endTime = oriEndTime
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime <= tableDataEndTime:
                startTime = oriStartTime
                endTime = minusOneDay(tableDataStartTime)
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime > tableDataEndTime:
                timeArray.append([oriStartTime, minusOneDay(tableDataStartTime)])
                timeArray.append([addOneDay(tableDataEndTime), oriEndTime])
        return timeArray

