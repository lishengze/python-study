# -*- coding: UTF-8 -*-
import sys
import pymssql  
from CONFIG import *
from toolFunc import *

reload(sys)
sys.setdefaultencoding('utf-8')

class Database:
    def __init__(self, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        self.__name__ = "Database"
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
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
        result = self.cur.execute(sql)  
        self.conn.commit()  

    def dropTableByName(self, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "drop table " + complete_tablename 
        self.changeDatabase(sql_str)

    def get_create_str(self,table_name):
        pass

    def get_insert_str(self,oridata, table_name):
        pass

    def createTableByName(self, table_name):
        create_str = self.get_create_str(table_name)
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
        insert_str = self.get_insert_str(oridata, table_name)
        self.changeDatabase(insert_str)

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

