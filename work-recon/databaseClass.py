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

    def ExecQuery(self,sql):  
        """ 
        执行查询语句 
        返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段 
 
        调用示例： 
                ms = MSSQL(host="localhost",user="sa",pwd="123456",db="PythonWeiboStatistics") 
                resList = ms.ExecQuery("SELECT id,NickName FROM WeiBoUser") 
                for (id,NickName) in resList: 
                    print str(id),NickName 
        """  
        self.cur.execute(sql)  
        result = self.cur.fetchall()  
        return result  
  
    def ExecStoreProduce(self,sql):  
        result = self.cur.execute(sql)  
        self.conn.commit()  

    def CloseConnect(self):
        self.conn.close()  

    def dropTableByName(self, tableName, logFile):
        try:
            # valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
            #             TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
            #             VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
            sqlStr = "drop table " + tableName 
            self.ExecStoreProduce(sqlStr)
        except:
            raise(e)  

    def createTableByName(databaseObj, tableName, logFile):
        try:
            valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
                        TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
                        VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
            sqlStr = "create table " + tableName + valueStr
            databaseObj.ExecStoreProduce(sqlStr)
        except:
            exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
            infoStr = "[X] createTableByName  Failed \n" \
                    + "[E] Exception :  \n" + exceptionInfo
            LogInfo(logFile, infoStr)  
            raise(Exception(infoStr))  

    def completeDatabaseTable (databaseName, tableNameArray, logFile):
        try:
            databaseObj = MSSQL() 
            tableInfo = getDatabaseTableInfo(databaseName, logFile)
            for tableName in tableNameArray:
                completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'
                if tableName not in tableInfo:
                    createTableByName(databaseObj, completeTableName, logFile)
            databaseObj.CloseConnect()
        except Exception as e:
            exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
            infoStr = "refreshTestDatabase Failed \n" \
                    + "[E] Exception :  \n" + exceptionInfo
            LogInfo(logFile, infoStr) 
            raise(Exception(infoStr))

    def refreshDatabase(databaseName, tableNameArray, logFile):
        try:
            databaseObj = MSSQL() 
            tableInfo = getDatabaseTableInfo(databaseName, logFile)
            for tableName in tableNameArray:
                completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'

                if tableName in tableInfo:
                    dropTableByName(databaseObj, completeTableName, logFile)
                    # print completeTableName
                createTableByName(databaseObj, completeTableName, logFile)
            databaseObj.CloseConnect()
        except Exception as e:
            exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
            infoStr = "refreshTestDatabase Failed \n" \
                    + "[E] Exception :  \n" + exceptionInfo
            LogInfo(logFile, infoStr)   
            raise(infoStr)      

    def refreshHistDatrabase(databaseName, tableNumb, logFile):
        try:
            databaseObj = MSSQL() 
            tableInfo = getDatabaseTableInfo(databaseName, logFile)
            # print tableInfo
            for i in range(tableNumb):
                tableName = str(i)
                completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'

                if tableName in tableInfo:
                    dropTableByName(databaseObj, completeTableName, logFile)
                    # print completeTableName
                createTableByName(databaseObj, completeTableName,logFile)
            databaseObj.CloseConnect()
        except Exception as e:
            exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
            infoStr = "refreshTestDatabase Failed \n" \
                    + "[E] Exception :  \n" + exceptionInfo
            LogInfo(logFile, infoStr) 
            raise(infoStr)

    def getDatabaseTableInfo(databaseName, logFile):
        try:
            databaseObj = MSSQL()
            queryString = "select name from "+ databaseName +"..sysobjects where xtype= 'U'"
            result = databaseObj.ExecQuery(queryString)
            transRst = []
            for i in range(len(result)):
                transRst.append(str(result[i][0]))
            databaseObj.CloseConnect()
            return transRst    
        except Exception as e:
            exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
            infoStr = "[X] GetDatabaseTableInfo Failed \n" \
                    + "[E] Exception :  \n" + exceptionInfo
            LogInfo(logFile, infoStr)    
            raise(Exception(infoStr)) 

    def getTableDataStartEndTime(databaseObj, databaseName, table):
        try:
            completeTableName = u'[' + databaseName + '].[dbo].['+ table +']'
            sqlStr = "SELECT MIN(TDATE), MAX(TDATE) FROM"  + completeTableName
            result = databaseObj.ExecQuery(sqlStr)
            startTime = result[0][0]
            endTime = result[0][1]
            return (startTime, endTime)
        except Exception as e:
            raise(e)

    def addPrimaryKey(database, logFile):
        try:
            databaseObj = MSSQL() 
            databaseTableInfo = getDatabaseTableInfo(database,logFile)
            for table in databaseTableInfo:
                completeTableName = u'[' + database + '].[dbo].['+ table +']'
                alterNullColumnSqlStr = "alter table "+ completeTableName +" alter column TDATE int not null\
                                    alter table "+ completeTableName +" alter column TIME int not null"
                
                databaseObj.ExecStoreProduce(alterNullColumnSqlStr)
                addPrimaryKeySqlStr = " alter table "+ completeTableName +" add primary key (TDATE, TIME)"
                databaseObj.ExecStoreProduce(addPrimaryKeySqlStr)
            databaseObj.CloseConnect()
        except Exception as e:
            exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
            infoStr = "AddPrimaryKey Failed \n" \
                    + "[E] Exception :  \n" + exceptionInfo  
            raise(Exception(infoStr))        