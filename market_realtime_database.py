# -*- coding: UTF-8 -*-
from CONFIG import *
from toolFunc import *
from database import Database

class MarketRealTimeDatabase(Database):
    def __init__(self, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, host, user, pwd, db)

    def __del__(self):
        Database.__del__(self)

    def get_create_str(self, table_name):
        value_str = "(股票 varchar(15), 日期 int not null, 时间 int not null Primary Key(股票), \
                      现价 decimal(15,4), 前收 decimal(15,4), 成交额 decimal(25,4))"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        # print create_str
        return create_str

    def get_update_str(self, oridata, table_name):
        col_str = "(日期, 时间, 现价, 前收, 成交额)"
        date = int(oridata[0])
        time = int(oridata[1])
        last = oridata[2]
        pre_close = oridata[3]
        amt = oridata[4]
        secode = oridata[5]

        set_str = "  set 日期 = " +  str(date) + ", 时间 = " + str(time) \
                + ", 现价 = " + str(last) + ", 成交额 = " + str(amt) \
                + " where 股票 = " + secode

               
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        insert_str = "update "+ complete_tablename + set_str 

    def get_insert_str(self, oridata, table_name):
        col_str = "(股票, 日期, 时间, 现价, 前收, 成交额)"
        date = int(oridata[0])
        time = int(oridata[1])
        last = oridata[2]
        pre_close = oridata[3]
        amt = oridata[4]
        secode = oridata[5]

        val_str = "\'" + str(secode) + "\', " + str(date) + ", " + str(time) + ", "+ str(last) + "," \
                + str(pre_close) + ", " + str(amt) + ""
               
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        insert_str = "insert into "+ complete_tablename + col_str + "values ("+ val_str +")"
        # print insert_str
        return insert_str        

    def get_check_str(self, colname, keyvalue, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        check_str = "select * from "  + complete_tablename + "where " + colname + " = " + "\'" + keyvalue + " \'"
        return check_str

    def check_data(self, colname, keyvalue, table_name):
        check_str = self.get_check_str(colname, keyvalue, table_name)
        result = self.get_database_data(check_str)
        if len(result) > 0:
            return True
        else 
            return False

    def update_data (self, oridata, table_name):
        update_str = self.get_update_str(oridata, table_name)
        self.changeDatabase(update_str)


