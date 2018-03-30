# -*- coding: UTF-8 -*-
from CONFIG import *
from toolFunc import *
from database import Database

class MarketDatabase(Database):
    def __init__(self, id=0, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, id, host, user, pwd, db)

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
            if TYClOSE != 0:
                PCTCHG = (TCLOSE - TYClOSE) / TYClOSE
            else:
                PCTCHG = 0

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
                    VATRUNOVER decimal(28,4), VOTRUNOVER decimal(28,4), PCTCHG decimal(10,4), YCLOSE decimal(15, 4), TURNOVER decimal(15, 4))"

        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        return create_str

    def get_insert_str(self, oridata, table_name):
        try:
            col_str = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG, YCLOSE, TURNOVER) "
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
            if len(oridata) >= 10:
                TURNOVER = oridata[9]
            else:
                TURNOVER = -1
            if TYClOSE != 0:
                PCTCHG = (TCLOSE - TYClOSE) / TYClOSE
            else:
                PCTCHG = 0

            val_str = TDATE + ", " + TIME + ", \'"+ SECODE + "\'," \
                    + str(TOPEN) + ", " + str(TCLOSE) + ", " + str(HIGH) + ", " + str(LOW) + ", " \
                    + str(VATRUNOVER) + ", " + str(VOTRUNOVER) + ", " + str(PCTCHG) + ", " + str(TYClOSE) + ", " + str(TURNOVER)

            complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
            insert_str = "insert into "+ complete_tablename + col_str + "values ("+ val_str +")"
            return insert_str      
        except Exception as e:
            error = "cannot concatenate"
            exception_info = "\n" + str(traceback.format_exc()) + '\n'
            if error in exception_info:
                print "oridata: ", oridata
            raise(Exception(exception_info)) 

    def get_multi_insert_str(self, oridataArray, table_name):
        try:
            col_str = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG, YCLOSE, TURNOVER) "
            val_str = ""
            for oridata in oridataArray:
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
                if len(oridata) >= 10:
                    TURNOVER = oridata[9]
                else:
                    TURNOVER = -1
                if TYClOSE != 0:
                    PCTCHG = (TCLOSE - TYClOSE) / TYClOSE
                else:
                    PCTCHG = 0

                val_str += "(" + TDATE + ", " + TIME + ", \'"+ SECODE + "\'," \
                         + str(TOPEN) + ", " + str(TCLOSE) + ", " + str(HIGH) + ", " + str(LOW) + ", " \
                         + str(VATRUNOVER) + ", " + str(VOTRUNOVER) + ", " + str(PCTCHG) + ", " \
                         + str(TYClOSE) + ", " + str(TURNOVER) +"),"

            val_str = val_str[0: (len(val_str)-1)]

            complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
            insert_str = "insert into "+ complete_tablename + col_str + "values "+ val_str
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

    def get_histdata_by_enddate(self, enddate, table_name, cloumn_str="*"):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "select "+ cloumn_str + " from " + complete_tablename \
                + " where TDATE <= " + str(enddate) + " order by TDATE, TIME;"
        data = self.get_database_data(sql_str)
        return data

    def update_restore_data(self, table_name, restore_data):
        col_str = "(TCLOSE, YCLOSE)"
        for item in restore_data:
            date = item[0]
            time = item[1]
            close = item[2]
            yclose = item[4]

            set_str = " set TCLOSE = " +  str(close) + ", YCLOSE = " + str(yclose) \
                    + " where TDATE = " + str(date) + " and TIME = " + str(time)
            complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
            update_str = "update "+ complete_tablename + set_str 
            self.changeDatabase(update_str)

    def getTableDataStartEndTime(self, table_name):
        startdatetime = None
        enddatetime = None
        tablename_array = self.getDatabaseTableInfo()
        if table_name in tablename_array:          
            complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
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

    def getStartEndDate(self, table_name):        
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        get_date_sqlstr = "SELECT MIN(TDATE), MAX(TDATE) FROM"  + complete_tablename
        date = self.get_database_data(get_date_sqlstr)
        return date[0]

    def getStartEndTime(self, oriStartTime, oriEndTime, tableDataStartTime, tableDataEndTime):
        timeArray = []
        if tableDataStartTime is None or tableDataEndTime is None:
            timeArray.append([oriStartTime, oriEndTime])
        else:
            if oriStartTime >=  tableDataStartTime and oriEndTime > tableDataEndTime:
                # startTime = addOneDay(tableDataEndTime)
                startTime = tableDataEndTime
                endTime = oriEndTime
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime <= tableDataEndTime:
                startTime = oriStartTime
                # endTime = minusOneDay(tableDataStartTime)
                endTime = tableDataStartTime
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime > tableDataEndTime:
                # timeArray.append([oriStartTime, minusOneDay(tableDataStartTime)])
                # timeArray.append([addOneDay(tableDataEndTime), oriEndTime])

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

    def getFirstData(self, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "select * from" + complete_tablename + \
                  "where TDATE = (select min(TDATE) from " + complete_tablename + ")"
        data = self.get_database_data(sql_str)

        if len(data) > 0:
            min_time = int(data[0][1])
            result = data[0]
            for item in data:
                if int(item[1]) < min_time:
                    result = item
            return result
        else:
            return data

    def getALLFirstData(self, tablename_array):
        result = {}
        for table_name in tablename_array:
            result[table_name] = self.getFirstData(table_name)
        return result
    
    def getTimeData(self, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "select TDATE, TIME from " + complete_tablename 
        data = self.get_database_data(sql_str)  
        return data    

    def getTimeDataCount(self, table_name, startdate, enddate):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "select count(*) from " + complete_tablename \
                + " where TDATE <= " + str(enddate) + " and TDATE >= " + str(startdate)
        data = self.get_database_data(sql_str)
        return data          

    def getAllLatestData(self, tablename_array):
        result = {}
        for table_name in tablename_array:
            result[table_name] = self.getLatestData(table_name)
        return result

    def get_data_bykey(self, key_list, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        key_str = ""
        for key in key_list:
            key_str += key + ","
        key_str = key_str[0 : (len(key_str)-1)]

        sql_str = "select " + key_str + " from " + complete_tablename + " order by TDATE, TIME"
        # print sql_str
        data = self.get_database_data(sql_str)  
       
        return data    

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
        # print ori_startdate, ori_enddate
        # print tabledata_startdate, tabledata_enddate
        # print transed_time_array
        for i in range(len(transed_time_array)):
            transed_time_array[i].insert(0, secode)       
        return transed_time_array