# -*- coding: UTF-8 -*-
from CONFIG import *
from func_tool import *
from database import Database

class FundamentalDatabase(Database):
    def __init__(self, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, host, user, pwd, db)

    def __del__(self):
        Database.__del__(self)

    def get_create_str(self, table_name, database_name = ""):
        if database_name == "":
            database_name = self.db
        value_str = "(股票代码 varchar(10) not null Primary Key(股票代码), 日期 int not null , \
                    市盈增长率 decimal(28,4), 市盈率 decimal(28,4), \
                    市净率 decimal(28,4), 市销率 decimal(28,4), \
                    每股现金流量净额 decimal(28,4), 每股收益 decimal(28,4), \
                    总市值 decimal(28,4),  净资产收益率 decimal(28,4))"
        complete_tablename = "[%s].[dbo].[%s]" % (database_name, str(table_name))
        create_str = "create table %s %s" % (complete_tablename, value_str)
        return create_str

    def get_insert_str(self, oridata, table_name, database_name = ""):
        if database_name == "":
            database_name = self.db        
        col_str = "(股票代码, 日期, 市盈增长率, 市盈率, 市净率, 市销率, 每股现金流量净额, \
                    每股收益, 总市值, 净资产收益率) "
 
        val_str = "('%s', %s, %s, %s, %s, %s, %s, %s, %s, %s) " % \
                    (oridata[0], oridata[1], oridata[2], oridata[3],oridata[4],\
                     oridata[5], oridata[6], oridata[7], oridata[8],oridata[9])

        complete_tablename = "[%s].[dbo].[%s]" % (database_name, str(table_name))
        insert_str = "insert into %s %s values %s" % (complete_tablename, col_str, val_str)
        return insert_str        

    def get_transed_conditions(self, table_name, source_conditions):
        trans_conditons = []        
        database_tableinfo = self.getDatabaseTableInfo()
        if table_name not in database_tableinfo:            
            trans_conditons.append(source_conditions)
        return trans_conditons