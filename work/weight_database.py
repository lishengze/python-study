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
        value_str = "(indexcode varchar(10), indexname varchar(50), indexcomday int, \
                    indexendday int not null, stockcode varchar(10) not null Primary Key(indexendday, stockcode), \
                    stockname varchar(50), ratio decimal(10,4), ranking int, datasource varchar(50))"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        return create_str

    def get_insert_str(self, oridata, table_name):
        col_str = " (indexcode, indexname, indexcomday, indexendday, stockcode, stockname, ratio, ranking, datasource)"
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
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "SELECT MIN(indexendday), MAX(indexendday) FROM"  + complete_tablename
        result = self.get_database_data(sql_str)
        startTime = result[0][0]
        endTime = result[0][1]
        return (startTime, endTime)  