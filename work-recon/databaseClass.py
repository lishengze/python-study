#coding=utf-8

import pymssql  
from CONFIG import *
  
class Database:  
    def __init__(self, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):  
        self.__name__ = "MSSQL"
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.conn = pymssql.connect(host=self.host,user=self.user,password=self.pwd,database=self.db,timeout=5,login_timeout=2,charset="utf8")  
        self.cur = self.conn.cursor()  
        if not self.cur:  
            raise(NameError,"Connect Data Base Failed! ")  
        # print (self.host, self.user, self.pwd, self.db)

    def __del__(self):
        self.closeConnect()

    def getData(self,sql):  
        self.cur.execute(sql)  
        result = self.cur.fetchall()  
        return result  
  
    def changeDatabase(self,sql):  
        result = self.cur.execute(sql)  
        self.conn.commit()  

    def closeConnect(self):
        self.conn.close()  

    def dropTableByName(self, tableName):
        sqlStr = "drop table " + tableName 
        self.changeDatabase(sqlStr)

    def createTableByName(self, tableName):
        valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
                    TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
                    VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
        sqlStr = "create table " + tableName + valueStr
        self.changeDatabase(sqlStr)

    def completeDatabaseTable (self, databaseName, tableNameArray):
        tableInfo = self.getDatabaseTableInfo(databaseName)
        for tableName in tableNameArray:
            completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'
            if tableName not in tableInfo:
                self.createTableByName(completeTableName)

    def refreshDatabase(self, databaseName, tableNameArray):
        tableInfo = getDatabaseTableInfo(databaseName)
        for tableName in tableNameArray:
            completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'

            if tableName in tableInfo:
                self.dropTableByName(completeTableName)
            self.createTableByName(completeTableName)    

    def refreshHistDatrabase(self, databaseName, tableNumb):
        tableInfo = getDatabaseTableInfo(databaseName)
        # print tableInfo
        for i in range(tableNumb):
            tableName = str(i)
            completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'

            if tableName in tableInfo:
                dropTableByName(completeTableName)
                # print completeTableName
            createTableByName(completeTableName)

    def getDatabaseTableInfo(self, databaseName):
        queryString = "select name from "+ databaseName +"..sysobjects where xtype= 'U'"
        result = self.getData(queryString)
        transRst = []
        for i in range(len(result)):
            transRst.append(str(result[i][0]))
        return transRst    

    def getTableDataStartEndTime(self, databaseName, table):
        completeTableName = u'[' + databaseName + '].[dbo].['+ table +']'
        sqlStr = "SELECT MIN(TDATE), MAX(TDATE) FROM"  + completeTableName
        result = self.getData(sqlStr)
        startTime = result[0][0]
        endTime = result[0][1]
        return (startTime, endTime)

    def addPrimaryKey(self, database):
        databaseTableInfo = getDatabaseTableInfo(database)
        for table in databaseTableInfo:
            completeTableName = u'[' + database + '].[dbo].['+ table +']'
            alterNullColumnSqlStr = "alter table "+ completeTableName +" alter column TDATE int not null\
                                alter table "+ completeTableName +" alter column TIME int not null"                
            self.changeDatabase(alterNullColumnSqlStr)

            addPrimaryKeySqlStr = " alter table "+ completeTableName +" add primary key (TDATE, TIME)"
            self.changeDatabase(addPrimaryKeySqlStr)