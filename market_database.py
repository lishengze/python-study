# -*- coding: UTF-8 -*-
from CONFIG import *
from toolFunc import *
from database import Database

class MarketDatabase(Database):
    def __init__(self, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, host, user, pwd, db)

    def __del__(self):
        Database.__del__(self)

    def get_create_str_old(self, table_name):
        value_str = "(TDATE int not null, TIME int not null Primary Key(TDATE, TIME), SECODE varchar(10), \
                    TOPEN decimal(15,4), TCLOSE decimal(15,4), HIGH decimal(15,4), LOW decimal(15,4), \
                    VATRUNOVER decimal(28,4), VOTRUNOVER decimal(28,4), PCTCHG decimal(10,4))"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        return create_str

    def get_insert_str_old(self, oridata, table_name):
        try:
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
        except Exception as e:
            error = "cannot concatenate"
            exception_info = "\n" + str(traceback.format_exc()) + '\n'
            if error in exception_info:
                print "oridata: ", oridata
            raise(Exception(exception_info))
           
    def get_create_str(self, table_name):
        value_str = "(TDATE int not null, TIME int not null Primary Key(TDATE, TIME), SECODE varchar(10), \
                    TOPEN decimal(15,4), TCLOSE decimal(15,4), HIGH decimal(15,4), LOW decimal(15,4), \
                    VATRUNOVER decimal(28,4), VOTRUNOVER decimal(28,4), PCTCHG decimal(10,4), YCLOSE decimal(15, 4))"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        return create_str

    def get_insert_str(self, oridata, table_name):
        try:
            col_str = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG, YCLOSE) "
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
                    + str(VATRUNOVER) + ", " + str(VOTRUNOVER) + ", " + str(PCTCHG) + ", " + str(TYClOSE)

            complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
            insert_str = "insert into "+ complete_tablename + col_str + "values ("+ val_str +")"
            return insert_str      
        except Exception as e:
            error = "cannot concatenate"
            exception_info = "\n" + str(traceback.format_exc()) + '\n'
            if error in exception_info:
                print "oridata: ", oridata
            raise(Exception(exception_info)) 

    def get_histdata_bytime(self, startdate, enddate, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "select * from " + complete_tablename \
                + " where TDATE <= " + enddate + " and TDATE >= " + startdate
        data = self.get_database_data(sql_str)
        return data

    def getTableDataStartEndTime(self, table_name):
        starttime = None
        endtime = None
        tablename_array = self.getDatabaseTableInfo()
        if table_name in tablename_array:          
            complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
            get_date_sqlstr = "SELECT MIN(TDATE), MAX(TDATE) FROM"  + complete_tablename
            date = self.get_database_data(get_date_sqlstr)

            if date[0][0] == None or date[0][1] == None:
                return (starttime, endtime)
            
            startdate = float(date[0][0])
            enddate = float(date[0][1])

            get_starttime_sqlstr = "SELECT MIN(TIME) FROM"  + complete_tablename + ' where TDATE='+str(startdate)            
            starttime = self.get_database_data(get_starttime_sqlstr)
            starttime = float(starttime[0][0])

            get_endtime_sqlstr = "SELECT MAX(TIME) FROM"  + complete_tablename + ' where TDATE='+str(enddate)
            endtime = self.get_database_data(get_endtime_sqlstr)
            endtime = float(endtime[0][0])

            # print startdate, starttime, enddate, endtime

            starttime = startdate + getpercenttime(starttime)
            endtime = enddate + getpercenttime(endtime)

            # print starttime, endtime
        return (starttime, endtime)

    def getStartEndTime(self, oriStartTime, oriEndTime, tableDataStartTime, tableDataEndTime):
        timeArray = []
        if tableDataStartTime is None or tableDataEndTime is None:
            timeArray.append([oriStartTime, oriEndTime])
        else:
            if oriStartTime >=  tableDataStartTime and oriEndTime > tableDataEndTime:
                startTime = tableDataEndTime
                endTime = oriEndTime
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime <= tableDataEndTime:
                startTime = oriStartTime
                endTime = tableDataStartTime
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime > tableDataEndTime:
                timeArray.append([oriStartTime, tableDataStartTime])
                timeArray.append([tableDataEndTime, oriEndTime])
        return timeArray

    def getLatestData(self, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "select * from" + complete_tablename + \
                  "where TDATE = (select max(TDATE) from " + complete_tablename + ")"
        data = self.get_database_data(sql_str)

        if len(data) > 0:
            max_time = int(data[0][1])
            result = data[0]
            for item in data:
                if int(item[1]) > max_time:
                    result = item
            return result
        else:
            return data

    def getAllLatestData(self, tablename_array):
        result = {}
        for table_name in tablename_array:
            result[table_name] = self.getLatestData(table_name)
        return result

    def addPrimaryKey(self):
        databaseTableInfo = self.getDatabaseTableInfo()
        for table in databaseTableInfo:
            complete_tablename = u'[' + self.db + '].[dbo].['+ table +']'
            alterNullColumnsql_str = "alter table "+ complete_tablename +" alter column TDATE int not null\
                                alter table "+ complete_tablename +" alter column TIME int not null"                
            self.changeDatabase(alterNullColumnsql_str)

            addPrimaryKeysql_str = " alter table "+ complete_tablename +" add primary key (TDATE, TIME)"
            self.changeDatabase(addPrimaryKeysql_str)    

    def get_transed_conditions(self, table_name, source_conditions):
        secode = table_name
        ori_startdate = source_conditions[1]
        ori_enddate = source_conditions[2]
        tabledata_startdate, tabledata_enddate = self.getTableDataStartEndTime(table_name)
        transed_time_array  = self.getStartEndTime(ori_startdate, ori_enddate, tabledata_startdate, tabledata_enddate)
        for i in range(len(transed_time_array)):
            transed_time_array[i].insert(0, secode)       
        return transed_time_array