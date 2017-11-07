# -*- coding: UTF-8 -*-
from CONFIG import *
from toolFunc import *

class MarketDatabaseFunc(object):
    def __init__(self, database_name):
        self.db = database_name

    def get_create_str(self, table_name):
        value_str = "(TDATE int, TIME int, SECODE varchar(10), \
                    TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
                    VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        return create_str

    def get_insert_str(self, oridata, table_name):
        col_str = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
        TDATE = getSimpleDate(oridata[0])
        TIME = getSimpleTime(oridata[0])
        SECODE = oridata[1]
        TOPEN = oridata[2]
        TCLOSE = oridata[3]
        HIGH = oridata[4]
        LOW = oridata[5]
        VOTRUNOVER = oridata[6]
        VATRUNOVER = oridata[7]
        TYClOSE = oridata[8]
        PCTCHG = (TCLOSE - TYClOSE) / TYClOSE

        val_str = TDATE + ", " + TIME + ", \'"+ SECODE + "\'," \
                + str(TOPEN) + ", " + str(TCLOSE) + ", " + str(HIGH) + ", " + str(LOW) + ", " \
                + str(VATRUNOVER) + ", " + str(VOTRUNOVER) + ", " + str(PCTCHG)

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        insert_str = "insert into "+ complete_tablename + col_str + "values ("+ val_str +")"
        return insert_str        