# -*- coding: UTF-8 -*-
from CONFIG import *
from toolFunc import *
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
        value_str = "(代码 varchar(25) not null Primary Key(代码))"
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        self.changeDatabase(create_str)
    
    def insertSecodeList(self, secodeList, tableName):
        col_str = " (代码)"
        complete_tablename = u'[' + self.db + '].[dbo].['+ tableName + ']'
        for secode in secodeList:            
            val_str = secode
            insert_str = "insert into "+ complete_tablename + col_str + "values ('"+ val_str +"')"
            # print insert_str
            self.changeDatabase(insert_str)