# -*- coding: UTF-8 -*-
import sys
import pymssql  
from CONFIG import *
from toolFunc import *
from weightdatabasefunc import WeightDatabaseFunc
from marketdatabasefunc import MarketDatabaseFunc

reload(sys)
sys.setdefaultencoding('utf-8')

class Database:
    def __init__(self, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        self.__name__ = "Database"
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.dbfunc = self.get_databasefunc()
        self.startConnect()

    def __del__(self):
        self.closeConnect()

    def startConnect(self):
        self.conn = pymssql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, \
                                    timeout=5, login_timeout=2, charset="utf8")
        self.cur = self.conn.cursor()
        if not self.cur:
            raise(NameError, "Connect Data Base Failed! ")

    def get_databasefunc(self):
        if "WeightData" in self.db:
            return WeightDatabaseFunc(self.db)
        
        if "MarketData" in self.db:
            return MarketDatabaseFunc(self.db)

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
        sql_str = "drop table " + table_name 
        self.changeDatabase(sql_str)

    def createTableByName(self, table_name):
        create_str = self.dbfunc.get_create_str(table_name)
        self.changeDatabase(create_str)

    def completeDatabaseTable (self, tableNameArray):
        table_info = self.getDatabaseTableInfo()
        for table_name in tableNameArray:            
            if table_name not in table_info:
                self.createTableByName(table_name)

    def refreshDatabase(self, tableNameArray):
        table_info = self.getDatabaseTableInfo()
        for table_name in tableNameArray:
            complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'

            if table_name in table_info:
                self.dropTableByName(complete_tablename)
            self.createTableByName(complete_tablename)    

    def insert_data(self, oridata, table_name):
        insert_str = self.dbfunc.get_insert_str(oridata, table_name)
        print insert_str
        self.changeDatabase(insert_str)
        # try:
        #     self.changeDatabase(insert_str)
        # except Exception as e:
        #     print str(traceback.format_exc())
        #     if "Violation of PRIMARY KEY constraint" not in e[1]:
        #         raise(e)

    def getDatabaseTableInfo(self):
        queryString = "select name from "+ self.db +"..sysobjects where xtype= 'U'"
        result = self.get_database_data(queryString)
        transRst = []
        for i in range(len(result)):
            transRst.append(str(result[i][0]))
        return transRst    

    def getTableDataStartEndTime(self, table):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table +']'
        sql_str = "SELECT MIN(TDATE), MAX(TDATE) FROM"  + complete_tablename
        result = self.get_database_data(sql_str)
        startTime = result[0][0]
        endTime = result[0][1]
        return (startTime, endTime)

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = 'select * from ' + complete_tablename
        result = self.get_database_data(sql_str)
        return result

    def getDataByTableName(self, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = 'select * from ' + complete_tablename
        result = self.get_database_data(sql_str)
        return result

    def addPrimaryKey(self):
        databaseTableInfo = self.getDatabaseTableInfo()
        for table in databaseTableInfo:
            complete_tablename = u'[' + self.db + '].[dbo].['+ table +']'
            alterNullColumnsql_str = "alter table "+ complete_tablename +" alter column TDATE int not null\
                                alter table "+ complete_tablename +" alter column TIME int not null"                
            self.changeDatabase(alterNullColumnsql_str)

            addPrimaryKeysql_str = " alter table "+ complete_tablename +" add primary key (TDATE, TIME)"
            self.changeDatabase(addPrimaryKeysql_str)