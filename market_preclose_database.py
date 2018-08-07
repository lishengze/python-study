# -*- coding: UTF-8 -*-
from CONFIG import *
from func_tool import *
from func_time import *
from database import Database

class MarketPreCloseDatabase(Database):
    def __init__(self, id=0, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, id, host, user, pwd, db)

    def __del__(self):
        Database.__del__(self)

    def get_create_str(self, table_name):
        value_str = "(股票 varchar(15) not null Primary Key(股票), 前收 decimal(15,4))"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        # print create_str
        return create_str

    def get_update_str(self, oridata, table_name):
        pre_close = oridata[0]
        secode = oridata[1]

        set_str = u"  set 前收 = " +  str(pre_close) + u" where 股票 = \'" + secode + "\'"

               
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        update_str = "update "+ complete_tablename + set_str 
        return update_str

    def get_insert_str(self, oridata, table_name):
        col_str = "(股票, 前收)"
        pre_close = oridata[0]
        secode = oridata[1]

        val_str = "\'" + str(secode) + "\', " + str(pre_close) 
               
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
        # print "result: ", result
        if len(result) > 0:
            return True
        else:
            return False

    def update_data (self, oridata, table_name):
        update_str = self.get_update_str(oridata, table_name)
        # print "update_str: ", update_str
        self.changeDatabase(update_str)


