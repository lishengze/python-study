# -*- coding: UTF-8 -*-
from CONFIG import *
from toolFunc import *
from database import Database

class WeightDatabase(Database):
    def __init__(self, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, host, user, pwd, db)

    def __del__(self):
        Database.__del__(self)

    def get_create_str(self, table_name):
        value_str = u"(指数代码 varchar(10), 指数名称 varchar(50), 指数成份日 int, \
                    指数截止日 int not null, 代码 varchar(10) not null Primary Key(指数截止日, 代码), \
                    名称 varchar(50), 比例 decimal(10,4), 排名 int, 数据来源 varchar(50))"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        return create_str

    def get_insert_str(self, oridata, table_name):
        col_str = " (指数代码, 指数名称, 指数成份日, 指数截止日, 代码, 名称, 比例, 排名, 数据来源)"
        val_str = "\'" + oridata[0] + "\', \'" + oridata[1] + "\', " \
                    + str(oridata[2]) + ", " + str(oridata[3]) + "," \
                    + "\'" + oridata[4] + "\', \'" + oridata[5] + "\', " \
                    + str(oridata[6]) + ", " + str(oridata[7]) + "," \
                    + "\'" + oridata[8] + "\'"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        insert_str = u"insert into " + complete_tablename + col_str + " values ("+ val_str +")"
        # print oridata
        # print insert_str
        return insert_str      

    def getTableDataStartEndTime(self, table_name):
        startTime = None
        endTime = None
        tablename_array = self.getDatabaseTableInfo()
        if table_name in tablename_array:            
            complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
            sql_str = "SELECT MIN(指数截止日), MAX(指数截止日) FROM"  + complete_tablename
            result = self.get_database_data(sql_str)
            startTime = result[0][0]
            endTime = result[0][1]
        return (startTime, endTime)  

    def get_transed_conditions(self, table_name, source_conditions):
        secode = table_name
        ori_startdate = source_conditions[1]
        ori_enddate = source_conditions[2]
        tabledata_startdate, tabledata_enddate = self.getTableDataStartEndTime(table_name)
        transed_time_array  = self.getStartEndTime(ori_startdate, ori_enddate, tabledata_startdate, tabledata_enddate)
        for i in range(len(transed_time_array)):
            transed_time_array[i].insert(0, secode)      
        return transed_time_array