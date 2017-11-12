# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime
import sys

from CONFIG import *
from toolFunc import *
from tinysoft import TinySoft
from database import Database

from weight_database import WeightDatabase
from market_database import MarketDatabase
from industry_database import IndustryDatabase

from weight_datanet import WeightTinySoft
from market_datanet import MarketTinySoft
from industry_datanet import IndustryNetConnect

reload(sys)
sys.setdefaultencoding('utf-8')

g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')
g_writeLogLock = threading.Lock()

def get_database_obj(database_name, host='localhost'):
    if "WeightData" in database_name:
        return WeightDatabase(host=host, db=database_name)

    if "MarketData" in database_name:
        return MarketDatabase(host=host, db=database_name)

def get_netconn_obj(database_type):
    if "WeightData" in database_type:
        return WeightTinySoft(database_type)

    if "MarketData" in database_type:
        return MarketTinySoft(database_type)     

def test_exec_tslstr():
    tinysoft_obj = TinySoft()

    industry_type = "申万"

    if industry_type == "申万":        
        indutry_name = u"申万行业"
        primary_industry_name = u"申万一级行业"
        second_industry_name = u"申万二级行业"
    
    if industry_type == "中证":
        indutry_name = u"中证证监会行业"
        primary_industry_name = u"中证一级行业"
        second_industry_name = u"中证二级行业"

    tsl_str = u"indutry_name:=\'" + indutry_name + "\'; \n \
        primary_industry_name := \'" + primary_industry_name + "\'; \n \
        second_industry_name := \'" + second_industry_name + "\'; \n \
        a := GetBkList(indutry_name); \n \
        r:=array(); \n \
        for i:=0 to length(a)-1 do \n  \
        begin \n  \
           primary_industry := a[i]; \n  \
           secondary_industry := getbklist(indutry_name+'\\\\'+ primary_industry);  //得到每个一级行业下的二级行业 \n \
           for j:=0 to length(secondary_industry)-1 do \n \
           begin \n \
                  tmp:=getbk(secondary_industry[j]); \n \
                  tmp:=select thisrow as '代码',primary_industry as primary_industry_name,secondary_industry[j] as second_industry_name from tmp end; \n \
                  r&=tmp;     //相当于r:=r union tmp; \n \
           end; \n \
        end; \n \
        return r; \n "
    # print tsl_str

    # tsl_str = u"name:='中证证监会行业';\
    #             return GetBklist2(name);"

    result = tinysoft_obj.test_tsl(tsl_str)
    print result[0:10]
    print len(result)

def test_getSecodeInfo():
    tinysoft_connect = TinySoft(g_logFile, g_writeLogLock)
    result = tinysoft_connect.getSecodeInfo()
    print len(result)
    # print result[1:10]
        
def test_get_weight_data():
    netconn_obj = get_netconn_obj('WeightData')
    source_array = netconn_obj.get_sourceinfo()
    start_date = 20101030
    end_date = 20101030
    for source in source_array:
        result = netconn_obj.get_netdata(source, start_date, end_date)
        if result == None:
            print "source: " + source + " has no data between " + str(start_date) + " and " + str(end_date)
            
    # if result is None:
    #     print secode + ' has no data between ' + str(start_date) + ' and ' + str(end_date)
    # else:
    #     print result[1:4]


    # print result
    # for secode in secode_array:
    #     result = tiny_obj.getWeightData(secode, start_date, end_date)
    #     print 'secode weight result len: ' + str(len(result))

def test_multi_thread_connect():
    try:
        thread_count = 2
        threads = []
        for i in range(thread_count):
            tmpThread = threading.Thread(target=TinySoft, args=(g_logFile, g_writeLogLock,))
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        exception_info = '\n' + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                + "TestMultiThread Failed" + "\n" \
                + "[E] Exception : \n" + exception_info
        # LogInfo(g_logFile, info_str) 
        raise(info_str)        

def test_connect():
    tinyConn = TinySoft()

def write_weightdata(database_obj, oridata, table_name):
    for item in oridata:
        database_obj.insert_data(item, table_name)
        
def test_singlethread_write_weightdata():
    database_name = "WeightDataTest"
    ori_startdate = 20171101
    ori_enddate = 20171103

    database_obj, tinysoft_obj = get_database_netconn_obj(database_name)
    source_array = tinysoft_obj.get_sourceinfo()
    # database_obj.completeDatabaseTable(source_array)
    database_obj.refreshDatabase(source_array)

    for source in source_array:
        result = tinysoft_obj.get_netdata(source, ori_startdate, ori_enddate)
        print len(result)
        write_weightdata(database_obj, result, source)

def test_industry():
    date = 20171109
    
    industry_obj = IndustryNetConnect()
    result = industry_obj.get_netdata(date)
    print len(result)
    print result[0]

    industry_database = IndustryDatabase(db="IndustryDataTest")
    # industry_database.completeDatabaseTable([date])
    for i in range(len(result)):
        industry_database.insert_data(result[i], date)

    # test_data = ['SH600000']
    # test_data.extend(result[0][1:len(result[0])])
    # print test_data

    # test_data_b = result[0]
    # test_data_b.extend(test_data)
    # print test_data_b

    # secode_info = industry_obj.get_allA_secode()
    # print len(secode_info)
    # print secode_info[0][0]


if __name__ == "__main__":
    try:
        # test_connect()
        # test_getSecodeInfo()
        # test_multi_thread_connect()
        # test_get_stockdata()
        # test_get_weight_data()
        # test_singlethread_write_weightdata()
        # test_exec_tslstr()
        test_industry()
    except Exception as exp:
        exception_info = '\n' + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                 + "__main__ Failed" + "\n" \
                 + "[E] Exception : " + exception_info
        LogInfo(g_logFile, info_str) 
