# -*- coding: UTF-8 -*-
from CONFIG import *
from toolFunc import *
from database import Database

class IndustryDatabase(Database):
    def __init__(self, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, host, user, pwd, db)

    def __del__(self):
        Database.__del__(self)

    def filter_source(self, source):
        database_tableNameArray = self.getDatabaseTableInfo()
        # print database_tableNameArray
        # print source
        filteredSource = []
        for tableName in source:
            if str(tableName) not in database_tableNameArray:
                filteredSource.append(tableName)
        return filteredSource

    def filter_tableArray(self, tableArray):
        return self.filter_source(tableArray)

    def get_create_str(self, table_name):
        value_str = "(日期 int not null , 股票代码 varchar(10) not null Primary Key(股票代码),  股票名称 varchar(50), \
                    中证一级行业 varchar(50), 中证二级行业 varchar(50), 中证三级行业 varchar(50), \
                    申万一级行业 varchar(50), 申万二级行业 varchar(50), 申万三级行业 varchar(50), \
                    万得一级行业 varchar(50), 万得二级行业 varchar(50), 万得三级行业 varchar(50), 万得四级行业 varchar(50))"

        complete_tablename = u'[' + self.db + '].[dbo].['+ str(table_name) +']'
        create_str = "create table " + complete_tablename + value_str
        return create_str

    def get_insert_str(self, oridata, table_name):
        col_str = "(日期, 股票代码, 股票名称,\
                    中证一级行业, 中证二级行业, 中证三级行业, \
                    申万一级行业, 申万二级行业, 申万三级行业, \
                    万得一级行业, 万得二级行业, 万得三级行业, 万得四级行业) "
 
        val_str = "" + str(oridata[0]) + ", \'" + oridata[1] + "\', \'" + oridata[2] + "\'," \
                + "\'" + oridata[3] + "\', \'" +  oridata[4] + "\', \'" + oridata[5] + "\'," \
                + "\'" + oridata[6] + "\', \'" +  oridata[7] + "\', \'"  +  oridata[8] + "\',"  \
                + "\'" + oridata[9] + "\', \'" +  oridata[10] + "\', \'"  +  oridata[11] + "\', \'" + oridata[12] + "\'"

        complete_tablename = u'[' + self.db + '].[dbo].['+ str(table_name) +']'
        insert_str = "insert into "+ complete_tablename + col_str + "values ("+ val_str +")"
        return insert_str        

    def get_transed_conditions(self, table_name, source_conditions):
        trans_conditons = []        
        database_tableinfo = self.getDatabaseTableInfo()
        if table_name not in database_tableinfo:            
            trans_conditons.append(source_conditions)
        return trans_conditons