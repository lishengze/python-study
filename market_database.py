from CONFIG import *
from func_tool import *
from func_time import *

from database import Database

class MarketDatabase(Database):
    def __init__(self, id=0, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, id, host, user, pwd, db)

    def __del__(self):
        Database.__del__(self)

    def get_create_str(self, table_name, database_name=""):
        if database_name == "":
            database_name = self.db        
        value_str = "(TDATE int not null, TIME int not null Primary Key(TDATE, TIME), SECODE varchar(10), \
                    TOPEN decimal(15,8), TCLOSE decimal(15,8), HIGH decimal(15,8), LOW decimal(15,8), \
                    VATRUNOVER decimal(28,4), VOTRUNOVER decimal(28,4), PCTCHG decimal(10,8), \
                    YCLOSE decimal(15, 8), TURNOVER decimal(15, 4), \
                    OpenRate decimal(10, 8), HighRate decimal(10, 8), LowRate decimal(10, 8))"

        complete_tablename = u'[' + database_name + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        return create_str

    def get_insert_str_old(self, oridata, table_name):
        try:
            col_str = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, \
                        VATRUNOVER, VOTRUNOVER, PCTCHG, YCLOSE, TURNOVER) "
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
                print ("oridata: ", oridata)
            raise(Exception(exception_info)) 

    def get_multi_insert_str_old(self, oridataArray, table_name):
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
                print ("oridata: ", oridata)
            raise(Exception(exception_info)) 

    def get_insert_str(self, oridata, table_name, database_name = ""):
        try:
            col_str = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, \
                        VATRUNOVER, VOTRUNOVER, PCTCHG, YCLOSE, TURNOVER, OpenRate, HighRate, LowRate) "

            # open_price  = oridata[3]
            # close_price = oridata[4]
            # high_price  = oridata[5]
            # low_price   = oridata[6]
            # open_rate   = open_price / close_price
            # high_rate   = high_price / close_price
            # low_rate    = low_price / close_price
            val_str = str(oridata[0]) + ", " + str(oridata[1]) + ", \'"+ str(oridata[2]) + "\'," \
                    + str(oridata[3]) + ", " + str(oridata[4]) + ", " + str(oridata[5]) + ", " \
                    + str(oridata[6]) + ", " + str(oridata[7]) + ", " + str(oridata[8]) + ", " \
                    + str(oridata[9]) + ", " + str(oridata[10]) + ", " + str(oridata[11]) + ', ' \
                    + str(oridata[12]) + ', ' + str(oridata[13]) + ', ' + str(oridata[14])

            if database_name == "":
                database_name = self.db

            complete_tablename = u'[' + database_name + '].[dbo].['+ table_name +']'
            insert_str = "insert into "+ complete_tablename + col_str + "values ("+ val_str +")"
            return insert_str      
        except Exception as e:
            error = "cannot concatenate"
            exception_info = "\n" + str(traceback.format_exc()) + '\n'
            if error in exception_info:
                print ("oridata: ", oridata)
            raise(Exception(exception_info)) 

    def get_update_str(self, oridata, table_name, database_name = ""):
        try:
            set_str = "TOPEN=%s, TCLOSE=%s, HIGH=%s, LOW=%s, VATRUNOVER=%s, VOTRUNOVER=%s, \
                       PCTCHG=%s, YCLOSE=%s, TURNOVER=%s, OpenRate=%s, HighRate=%s, LowRate=%s \
                       where TDATE=%s and TIME=%s" % \
                       (str(oridata[3]), str(oridata[4]), str(oridata[5]), str(oridata[6]),\
                        str(oridata[7]), str(oridata[8]), str(oridata[9]), str(oridata[10]), \
                        str(oridata[11]), str(oridata[12]), str(oridata[13]), str(oridata[14]), \
                        str(oridata[0]), str(oridata[1])) 

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

    def get_multi_insert_str(self, oridataArray, table_name, database_name = ""):
        try:
            col_str = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, \
                        LOW, VATRUNOVER, VOTRUNOVER, PCTCHG, YCLOSE, TURNOVER) "
            val_str = ""
            for oridata in oridataArray:
                if len(oridata) < 12:
                    print (oridata)

                # open_price  = oridata[3]
                # close_price = oridata[4]
                # high_price  = oridata[5]
                # low_price   = oridata[6]
                # open_rate   = open_price / close_price
                # high_rate   = high_price / close_price
                # low_rate    = low_price / close_price
                val_str += "(" + str(oridata[0]) + ", " + str(oridata[1]) + ", \'"+ str(oridata[2]) + "\'," \
                        + str(oridata[3]) + ", " + str(oridata[4]) + ", " + str(oridata[5]) + ", " \
                        + str(oridata[6]) + ", " + str(oridata[7]) + ", " + str(oridata[8]) + ", " \
                        + str(oridata[9]) + ", " + str(oridata[10]) + ", " + str(oridata[11]) + ', ' \
                        + str(oridata[12]) + ', ' + str(oridata[13]) + ', ' + str(oridata[14]) +"),"

            if database_name == "":
                database_name = self.db

            val_str = val_str[0: (len(val_str)-1)]
            complete_tablename = u'[' + database_name + '].[dbo].['+ table_name +']'
            insert_str = "insert into "+ complete_tablename + col_str + "values "+ val_str
            return insert_str      
        except Exception as e:
            error = "cannot concatenate"
            exception_info = "\n" + str(traceback.format_exc()) + '\n'
            if error in exception_info:
                print ("oridata: ", oridata)
            raise(Exception(exception_info)) 

    def get_histdata_bytime(self, start_date, end_date, table_name, value_list = ['*'], database_name=""):
        if database_name == "":
            database_name = self.db         
        value_str = ','.join(value_list)
        complete_tablename = u'[' + database_name + '].[dbo].['+ table_name +']'
        sql_str = "select %s from %s where TDATE <= %s and TDATE >= %s order by TDATE,TIME"  % \
                    (value_str, complete_tablename, str(end_date), str(start_date))
        data = self.get_database_data(sql_str)
        return data

    def get_date_data(self, startdate, enddate):
        secode = 'SH000300'
        result = self.get_histdata_by_date(startdate=startdate, enddate=enddate, \
                                            table_name=secode, cloumn_str='TDATE')
        return result

    def get_histdata_by_enddate(self, enddate, table_name, cloumn_str="*"):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "select "+ cloumn_str + " from " + complete_tablename \
                + " where TDATE <= " + str(enddate) + ' order by TDATE, TIME'
        data = self.get_database_data(sql_str)
        for i in range(len(data)):
            data[i] = list(data[i])                    
        return data

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

    def delete_data_by_date(self, startdate, enddate, table_name, database_name=""):
        if database_name == "":
            database_name = self.db 
        complete_tablename = u'[' + database_name + '].[dbo].['+ table_name +']'
        sql_str = 'delete from %s where TDATE >= %s and TDATE <= %s' % \
                    (complete_tablename,  str(startdate), str(enddate))
        data = self.get_database_data(sql_str)        

    def get_all_data(self, table_name, cloumn_str="*"):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "select "+ cloumn_str + " from " + complete_tablename \
                + " order by TDATE, TIME"
        data = self.get_database_data(sql_str)
        for i in range(len(data)):
            data[i] = list(data[i])
        return data      

    def get_data_by_enddatetime(self, table_name, enddate, cloumn_str="*"):
        end_date = enddate[0]
        end_time = enddate[1]
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "select "+ cloumn_str + " from " + complete_tablename \
                + " where TDATE <= " + str(end_date) + " order by TDATE, TIME"

        data = self.get_database_data(sql_str)
        for i in range(len(data)):
            data[i] = list(data[i])

        index = len(data) - 1
        while index >= 0 and int(data[index][0]) == int(end_date) and int(data[index][1]) >= int(end_time):   
            index -= 1                  
        return data[0:index+1]

    def delete_data_by_enddatetime(self, table_name, enddate, cloumn_str="*"):
        end_date = enddate[0]
        end_time = enddate[1]
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "delete from " + complete_tablename \
                + " where TDATE < " + str(end_date)
        self.changeDatabase(sql_str)

        sql_str = "delete from " + complete_tablename \
                + " where TDATE = " + str(end_date) + ' and TIME < ' + str(end_time)
        self.changeDatabase(sql_str)

    def delete_all_data(self, table_name):
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        sql_str = "delete from " + complete_tablename 
        self.changeDatabase(sql_str)

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

    def getStartEndDate(self, table_name):        
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        get_date_sqlstr = "SELECT MIN(TDATE), MAX(TDATE) FROM"  + complete_tablename
        date = self.get_database_data(get_date_sqlstr)
        return date[0]

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
            return list(result)
        else:
            return list(data)

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
            return list(result)
        else:
            return list(data)

    def get_first_date(self, table_name, database_name=""):
        if database_name=="":
            database_name = self.db
        complete_tablename = u'[' + database_name + '].[dbo].['+ table_name +']'
        sql_str = "select min(TDATE) from " + complete_tablename + ")"
        result = self.get_database_data(sql_str)
        return result

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

    def addPrimaryKey(self):
        databaseTableInfo = self.getDatabaseTableInfo()
        for table in databaseTableInfo:
            complete_tablename = u'[' + self.db + '].[dbo].['+ table +']'
            alterNullColumnsql_str = "alter table "+ complete_tablename +" alter column TDATE int not null\
                                alter table "+ complete_tablename +" alter column TIME int not null"                
            self.changeDatabase(alterNullColumnsql_str)

            addPrimaryKeysql_str = " alter table "+ complete_tablename +" add primary key (TDATE, TIME)"
            self.changeDatabase(addPrimaryKeysql_str)    

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

    