#coding=utf-8
import pymssql  
from CONFIG import *
from toolFunc import *
from weightdatabasefunc import WeightDatabaseFunc
from marketdatabasefunc import MarketDatabaseFunc

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

    def getData(self,sql):  
        self.cur.execute(sql)  
        result = self.cur.fetchall()  
        return result  
  
    def changeDatabase(self,sql):  
        result = self.cur.execute(sql)  
        self.conn.commit()  

    def dropTableByName(self, table_name):
        sqlStr = "drop table " + table_name 
        self.changeDatabase(sqlStr)

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

    def get_insert_weightdata_str(self, oridata, table_name):
        col_str = "(indexcode, indexname, indexcomday, indexendday, stockcode, stockname, ratio, ranking, datasource)"
        val_str = "\'" + oridata[0] + "\', \'" + oridata[1] + "\', " \
                    + str(oridata[2]) + ", " + str(oridata[3]) + "," \
                    + "\'" + oridata[4] + "\', \'" + oridata[5] + "\', " \
                    + str(oridata[6]) + ", " + str(oridata[7]) + "," \
                    + "\'" + oridata[8] + "\'"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        insert_str = "insert into " + complete_tablename + col_str + " values ("+ val_str +")"
        # print oridata
        # print insert_str
        return insert_str

    def get_insert_marketdata_str(self, oridata, table_name):
        col_str = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
        TDATE = getSimpleDate(oridata[0])
        TIME = getSimpleTime(oridata[0])
        SECODE = oridata[1]
        TOPEN = oridata[2]
        TCLOSE = oridata[3]
        HIGH = oridata[4]
        LOW = oridata[5]
        VOTRUNOVER = oridata[6]
        VATRUNOVER = oridata[7]
        TYClOSE = oridata[8]
        PCTCHG = (TCLOSE - TYClOSE) / TYClOSE

        val_str = TDATE + ", " + TIME + ", \'"+ SECODE + "\'," \
                + str(TOPEN) + ", " + str(TCLOSE) + ", " + str(HIGH) + ", " + str(LOW) + ", " \
                + str(VATRUNOVER) + ", " + str(VOTRUNOVER) + ", " + str(PCTCHG)

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        insert_str = "insert into "+ complete_tablename + col_str + "values ("+ val_str +")"
        return insert_str 

    def insert_data(self, oridata, table_name):
        # if "WeightData" in self.db:
        #     insert_str = self.get_insert_weightdata_str(oridata, table_name)
        # if "MarketData" in self.db:
        #     insert_str = self.get_insert_marketdata_str(oridata, table_name)
        insert_str = self.dbfunc.get_insert_str()
        try:
            self.changeDatabase(insert_str)
        except Exception as e:
            if "Violation of PRIMARY KEY constraint" not in e[1]:
                raise(e)

    def getDatabaseTableInfo(self):
        queryString = "select name from "+ self.db +"..sysobjects where xtype= 'U'"
        result = self.getData(queryString)
        transRst = []
        for i in range(len(result)):
            transRst.append(str(result[i][0]))
        return transRst    

    def getTableDataStartEndTime(self, table):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table +']'
        sqlStr = "SELECT MIN(TDATE), MAX(TDATE) FROM"  + complete_tablename
        result = self.getData(sqlStr)
        startTime = result[0][0]
        endTime = result[0][1]
        return (startTime, endTime)

    def getDataByTableName(self, table_name):
        sql_str = 'select * from ' + table_name
        result = self.getData(table_name)
        return result

    def addPrimaryKey(self):