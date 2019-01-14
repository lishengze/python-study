import sys
import pymssql  
from CONFIG import *
from func_tool import *
import time

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
        try:
            self.conn = pymssql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, \
                                        charset="utf8", timeout=300, login_timeout=300)
            self.cur = self.conn.cursor()
            if not self.cur:
                raise(NameError, "Connect Data Base Failed! ")
            else:
                print("Connect %s Success" % (self.host))
        except Exception as e:
            exception_info = str(traceback.format_exc())
            db_connect_error = '20002'
            if db_connect_error not in exception_info:
                raise(e)
            else:
                restart_time = 10
                print("[X] 链接数据库出错, %d s 后重新执行" % (restart_time))                   
                time.sleep(restart_time)
                self.startConnect()

    def closeConnect(self):
        self.conn.close()  

    def get_database_data(self,sql):          
        try:
            self.cur.execute(sql)  
            result = self.cur.fetchall() 
            return result
        except Exception as e:
            exception_info = str(traceback.format_exc())
            no_result_error = 'Statement not executed or executed statement has no resultset'
            db_connect_error = '20003'
            if db_connect_error in exception_info:
                return self.get_create_str(sql)
            elif no_result_error in exception_info:
                return []
            else:
                raise(e)

    def changeDatabase(self,sql):  
        # result1 = self.cur.execute(sql)  
        # result2 = self.conn.commit() 
        # return result1        
        try:
            result1 = self.cur.execute(sql)  
            result2 = self.conn.commit()  
            return result1
        except Exception as e:
            exception_info = str(traceback.format_exc())
            db_connect_error = '20003'
            if db_connect_error not in exception_info:
                raise(e)
            else:
                restart_time = 10
                print("[X] 执行数据库出错, %d s 后重新执行" % (restart_time))                
                time.sleep(10)
                return self.changeDatabase(sql)

    def dropTableByName(self, table_name, database_name=""):
        if database_name == "":
            database_name = self.db
        complete_tablename = u'[' + database_name + '].[dbo].['+ table_name +']'
        sql_str = "drop table " + complete_tablename 
        self.changeDatabase(sql_str)

    def clearDatabase(self, table_list=[], database_name=""):
        if database_name == "":
            database_name = self.db        
        all_table_list = self.getDatabaseTableInfo(database_name=database_name)
        if table_list == []:
            table_list = all_table_list

        for table_name in table_list: 
            if table_name in all_table_list:
                self.dropTableByName(table_name, database_name)        

    def get_create_str(self,table_name, database_name = ""):
        pass

    def get_insert_str(self,oridata, table_name, database_name = ""):
        pass

    def get_update_str(self,oridata, table_name, database_name = ""):
        pass        

    def filter_source(self, source):
        return source

    def filter_tableArray(self, tableArray):
        return tableArray

    def createTableByName(self, table_name, database_name=""):
        if database_name == "":
            database_name = self.db
        create_str = self.get_create_str(table_name, database_name)
        self.changeDatabase(create_str)

    def completeDatabaseTable (self, table_name_list, database_name=""):
        if database_name == "":
            database_name = self.db

        table_info = self.getDatabaseTableInfo(database_name)
        for table_name in table_name_list:            
            if table_name not in table_info:
                self.createTableByName(table_name, database_name)

    def refreshDatabase(self, table_name_list):
        table_info = self.getDatabaseTableInfo()
        for table_name in table_name_list:
            if table_name in table_info:
                self.dropTableByName(table_name)
            self.createTableByName(table_name)    

    def insert_data(self, oridata, table_name, database_name = ""):
        insert_str = self.get_insert_str(oridata, table_name, database_name)
        result = self.changeDatabase(insert_str)

        if result != None:
            connFailedWaitTime = 5
            print ('insert result: ', result)
            print ('\n[X] insert %s error, restart! \n' %(table_name))
            time.sleep(connFailedWaitTime)
            self.insert_data(oridata, table_name)
        return result

    def update_data(self, oridata, table_name, database_name = ""):
        update_str = self.get_update_str(oridata, table_name, database_name)
        result = self.changeDatabase(update_str)

        if result != None:
            connFailedWaitTime = 5
            print ('insert result: ', result)
            print ('\n[X] update %s error, restart! \n' %(table_name))
            time.sleep(connFailedWaitTime)
            self.insert_data(oridata, table_name)
        return result

    def insert_multi_data(self, oridataArray, table_name, database_name = ""):
        start_index = 0
        while start_index < len(oridataArray):
            end_index = start_index + self.insertDataNumbOnce
            if end_index > len(oridataArray):
                end_index = len(oridataArray)

            insert_str = self.get_multi_insert_str(oridataArray[start_index:end_index], table_name, database_name)
            self.changeDatabase(insert_str)
            
            start_index = end_index

    def get_datacount(self, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = 'select count(*) from ' + complete_tablename
        result = self.get_database_data(sql_str)
        return result[0][0]

    def check_table(self, table_name):
        table_list = self.getDatabaseTableInfo()
        if table_name in table_list:
            return True
        else:
            return False

    def getDatabaseTableInfo(self, database_name = ""):
        if database_name == "":
            database_name = self.db
        queryString = "select name from "+ database_name +"..sysobjects where xtype= 'U'"
        result = self.get_database_data(queryString)
        transRst = []
        for i in range(len(result)):
            transRst.append(str(result[i][0]))
        return transRst    

    def get_db_table_list(self, database_name = ""):
        if database_name == "":
            database_name = self.db
        queryString = "select name from "+ database_name +"..sysobjects where xtype= 'U'"
        result = self.get_database_data(queryString)
        transRst = []
        for i in range(len(result)):
            transRst.append(str(result[i][0]))
        return transRst    

    def get_amarket_secode_list(self):
        ori_secode_list = self.getDatabaseTableInfo()
        index_secode_list = get_index_code_list('tinysoft')
        for code in index_secode_list:
            if code in ori_secode_list:
                ori_secode_list.remove(code)
        return ori_secode_list

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

class TestDatabase(object):
    def __init__(self):
        self.__name__ = "TestDatabase"
        self.test_check_database_table_list()

    def test_check_database_table_list(self):
        database_obj = Database(host="192.168.211.162")
        table_list_day = database_obj.get_db_table_list("MarketData_day")
        table_list_10m = database_obj.get_db_table_list("MarketData_15m")
        print("table_list_day.size: %d, table_list_10m.size: %d" % (len(table_list_day), len(table_list_10m)))
        for table in table_list_day:
            if table not in table_list_10m:
                print(table)

if __name__ == "__main__":
    test_database_obj = TestDatabase()



    
    