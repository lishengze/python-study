# -*- coding: UTF-8 -*-
from CONFIG import *
from toolFunc import *
from database import Database

class IndustryDatabase(Database):
    def __init__(self, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, host, user, pwd, db)

    def __del__(self):
        Database.__del__(self)

    def get_create_str(self, table_name):
        value_str = "(Secode varchar(10) not null, Date int not null Primary Key(Secode), 中证一级行业 varchar(50), 中证二级行业 varchar(50), \
                    申万一级行业 varchar(50), 申万二级行业 varchar(50), 申万三级行业 varchar(50), \
                    万得一级行业 varchar(50), 万得二级行业 varchar(50), 万得三级行业 varchar(50), 万得四级行业 varchar(50))"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        return create_str

    def get_insert_str(self, oridata, table_name):
        col_str = "(Secode, Date, 中证一级行业, 中证二级行业, 申万一级行业, 申万二级行业, 申万三级行业, \
                    万得一级行业, 万得二级行业, 万得三级行业, 万得四级行业) "
 
        val_str = "\'" + oridata[0] + "\', " + str(oridata[1]) + "," \
                + "\'" + oridata[2] + "\', \'" +  oridata[3] + "\',"  \
                + "\'" + oridata[4] + "\', \'" +  oridata[5] + "\', \'"  +  oridata[6] + "\',"  \
                + "\'" + oridata[7] + "\', \'" +  oridata[8] + "\', \'"  +  oridata[9] + "\', \'" + oridata[10] + "\'"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        insert_str = "insert into "+ complete_tablename + col_str + "values ("+ val_str +")"
        return insert_str        
