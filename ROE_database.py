# -*- coding: UTF-8 -*-
from CONFIG import *
from func_tool import *
from database import Database

class ROEDatabase(Database):
    def __init__(self, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, host, user, pwd, db)

    def __del__(self):
        Database.__del__(self)

    def get_create_str(self, table_name, database_name = ""):
        if database_name == "":
            database_name = self.db

        value_str = "(TDATE int not null , TIME int not null,  ROE decimal(28,4) Primary Key(TDATE))"
        complete_tablename = "[%s].[dbo].[%s]" % ("ROEData", str(table_name))
        create_str = "create table %s %s" % (complete_tablename, value_str)

        return create_str

    def get_insert_str(self, oridata, table_name, database_name = ""):
        if database_name == "":
            database_name = self.db        
        
        col_str = "(TDATE, TIME, ROE)"
        val_str = "(%s, %s, %s) " % (oridata[0], oridata[1],  oridata[2])
        complete_tablename = "[%s].[dbo].[%s]" % ("ROEData", str(table_name))
        insert_str = "insert into %s %s values %s" % (complete_tablename, col_str, val_str)

        return insert_str

    def get_update_str(self, oridata, table_name, database_name = ""):
        try:
            set_str = "ROE=%s where TDATE=%s " % (str(oridata[2]),str(oridata[0])) 
            if database_name == "":
                database_name = self.db
                
            complete_tablename = u"[%s].[dbo].[%s]" % (database_name, table_name)
            update_str = "update %s set %s" %(complete_tablename, set_str)
            return update_str      
        except Exception as e:
            error = "cannot concatenate"
            exception_info = "\n" + str(traceback.format_exc()) + '\n'
            if error in exception_info:
                print ("oridata: ", oridata)
            raise(Exception(exception_info))  

    def get_histdata_by_date(self, startdate, enddate, table_name, value_list=['*'], database_name=""):
        if database_name == "":
            database_name = self.db 
        complete_tablename = u'[' + database_name + '].[dbo].['+ table_name +']'
        value_str = ','.join(value_list)
        sql_str = 'select %s from %s where TDATE >= %s and TDATE <= %s order by TDATE, TIME' % \
                    (value_str, complete_tablename,  str(startdate), str(enddate))
        data = self.get_database_data(sql_str)
        for i in range(len(data)):
            data[i] = list(data[i])                    
        return data

    def getTableDataStartEndTime(self, table_name, database_name=""):
        startdatetime = None
        enddatetime = None
        if database_name == "":
            database_name = self.db
        tablename_array = self.getDatabaseTableInfo(database_name)

        if table_name in tablename_array:          
            complete_tablename = u'[' + database_name + '].[dbo].['+ table_name +']'
            get_date_sqlstr = "SELECT MIN(TDATE), MAX(TDATE) FROM"  + complete_tablename
            date = self.get_database_data(get_date_sqlstr)

            if date[0][0] == None or date[0][1] == None:
                return (startdatetime, enddatetime)
            
            startdate = float(date[0][0])
            enddate = float(date[0][1])

            get_starttime_sqlstr = "SELECT MIN(TIME) FROM"  + complete_tablename + ' where TDATE='+str(startdate)            
            starttime = self.get_database_data(get_starttime_sqlstr)
            starttime = float(starttime[0][0])

            get_endtime_sqlstr = "SELECT MAX(TIME) FROM"  + complete_tablename + ' where TDATE='+str(enddate)
            endtime = self.get_database_data(get_endtime_sqlstr)
            endtime = float(endtime[0][0])

            # print startdate, starttime, enddate, endtime

            # startdatetime = startdate * 1000000 + starttime
            # enddatetime = enddate * 1000000 + endtime

            startdatetime = startdate
            enddatetime = enddate

            # print starttime, endtime
        return (startdatetime, enddatetime)

    def getStartEndTime(self, oriStartTime, oriEndTime, tableDataStartTime, tableDataEndTime):
        timeArray = []
        if tableDataStartTime is None or tableDataEndTime is None:
            timeArray.append([oriStartTime, oriEndTime, 'left'])
        else:
            if oriStartTime >=  tableDataStartTime and oriEndTime > tableDataEndTime:
                startTime = int(tableDataEndTime)
                endTime = oriEndTime
                timeArray.append([startTime, endTime, 'right'])
            
            if oriStartTime < tableDataStartTime and oriEndTime <= tableDataEndTime:
                startTime = oriStartTime
                endTime = int(tableDataStartTime)
                timeArray.append([startTime, endTime, 'left'])
            
            if oriStartTime < tableDataStartTime and oriEndTime > tableDataEndTime:
                timeArray.append([oriStartTime, int(tableDataStartTime), 'left'])
                timeArray.append([int(tableDataEndTime), oriEndTime, 'right'])

        return timeArray

    def get_transed_conditions(self, table_name, source_conditions,database_name=""):
        secode = table_name
        if len(source_conditions) == 2:
            ori_startdate = source_conditions[0]
            ori_enddate = source_conditions[1]

        if len(source_conditions) == 3:
            ori_startdate = source_conditions[1]
            ori_enddate = source_conditions[2]                    

        if database_name == "":
            database_name = self.db        
        tabledata_startdate, tabledata_enddate = self.getTableDataStartEndTime(table_name, database_name)
        transed_time_array  = self.getStartEndTime(ori_startdate, ori_enddate, \
                                                   tabledata_startdate, tabledata_enddate)
        for i in range(len(transed_time_array)):
            transed_time_array[i].insert(0, secode)       
        return transed_time_array        