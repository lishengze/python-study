# -*- coding: UTF-8 -*-
from CONFIG import *
from func_tool import *
from func_time import *
from func_secode import *
from database import Database

class MarketInfoDatabase(Database):
    def __init__(self, id=0, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db="Market_Info"):
        Database.__init__(self, id, host, user, pwd, db)

    def __del__(self):
        Database.__del__(self)

    def refreshSecodeListTable(self, table_name):
        table_info = self.getDatabaseTableInfo()
        if table_name in table_info:
            self.dropTableByName(table_name)
        self.createSecodeListTable(table_name)  

    def createSecodeListTable(self, table_name):
        value_str = "(代码 varchar(25) not null, 公司 varchar(50) not null, Primary Key(代码))"
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        self.changeDatabase(create_str)
    
    def insertSecodeList(self, ori_data, table_name):
        if self.check_table(table_name) == False:
            self.createSecodeListTable(table_name)

        col_str = " (代码, 公司)"
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name + ']'
        for item in ori_data:
            insert_str = "insert into %s %s values ('%s', '%s')" % (complete_tablename, col_str, item[0], item[1])
            # print(insert_str)
            try:
                self.changeDatabase(insert_str)
            except Exception as e:
                    exception_info = "\n" + str(traceback.format_exc()) + '\n'
                    duplicate_insert_error = "Violation of PRIMARY KEY constraint"
                    if duplicate_insert_error not in exception_info:
                        raise(e)
            
    def get_index_secode_list(self, table_name, style='ori'):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name  + '_SecodeList]'
        sql_str = u'select (代码) from %s' % (complete_tablename)
        data = self.get_database_data(sql_str)    
        result = []
        for item in data:
            result.append(get_complete_stock_code(item[0], style))   
        return result      

    def get_market_secode_list(self, market_name = "A_Market", style="ori"):
        complete_tablename = '[%s].[dbo].[%s]' % (self.db, market_name)
        sql_str = 'select (代码) from %s' % (complete_tablename)
        data = self.get_database_data(sql_str)    
        result = []
        for item in data:
            result.append(get_complete_stock_code(item[0], style))   
        return result  

    def create_dbinfo_table(self, table_name):
        value_str = "(代码 varchar(25) not null, Primary Key(代码))"
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        self.changeDatabase(create_str)        

    def insert_dbinfo(self, table_name, ori_data, database_name=""):
        if self.check_table(table_name) == False:
            self.create_dbinfo_table(table_name)

        col_str = " (代码) "
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name + ']'
        for item in ori_data:
            insert_str = "insert into %s %s values ('%s')" % (complete_tablename, col_str, item)
            try:
                self.changeDatabase(insert_str)
            except Exception as e:
                    exception_info = "\n" + str(traceback.format_exc()) + '\n'
                    duplicate_insert_error = "Violation of PRIMARY KEY constraint"
                    if duplicate_insert_error not in exception_info:
                        raise(e)        
    
def get_wind_markert_secode_list(market_name = "A_Market", dbhost = "192.168.211.162", style="ori"):
    marketinfo_obj = MarketInfoDatabase(host = dbhost)
    result = marketinfo_obj.get_market_secode_list(market_name=market_name, style=style)
    return result

class TestMarketInfoDatabase:
    def __init__(self):
        self.__name__ = "TestMarketInfoDatabase"
        self.test_get_wind_markert_secode_list()

    def test_get_wind_markert_secode_list(self):
        wind_a_market_code_list = get_wind_markert_secode_list(style="tinysoft")
        print_list("wind_a_market_code_list", wind_a_market_code_list)

if __name__ == "__main__":
    test_obj = TestMarketInfoDatabase()
    
