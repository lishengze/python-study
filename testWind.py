# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime
import time

from CONFIG import *
from func_tool import *
from wind import Wind
from WindPy import *
from market_realtime_database import MarketRealTimeDatabase
from market_preclose_database import MarketPreCloseDatabase

g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')
g_writeLogLock = threading.Lock()

def printpy(outdata):
    if outdata.ErrorCode!=0:
        print('error code:'+str(outdata.ErrorCode)+'\n');
        return();
    for i in range(0,len(outdata.Data[0])):
        strTemp=''
        if len(outdata.Times)>1:
            strTemp=str(outdata.Times[i])+' '
        for k in range(0, len(outdata.Fields)):
            strTemp=strTemp+str(outdata.Data[k][i])+' '
        print(strTemp)

def test_getSecodeInfo():
    tinysoft_connect = Wind(g_logFile, g_writeLogLock)
    result = tinysoft_connect.getSecodeInfo()
    print (len(result))
    print (result[1:10])
        
def test_get_stockdata():
    wind_connect = Wind(g_logFile, g_writeLogLock)
    secode = "600000.SH"
    start_date = '20171107 093100'
    end_date = '20171107 093200'
    result = wind_connect.getStockData(secode, start_date, end_date)
    if result is None:
        print (secode + ' has no data between ' + str(start_date) + ' and ' + str(end_date))
    else:
        printpy(result)
        # print result[1]

def test_multi_thread_connect():
    thread_count = 2
    threads = []
    for i in range(thread_count):
        tmpThread = threading.Thread(target=Wind, args=(g_logFile, g_writeLogLock,))
        threads.append(tmpThread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()     

def test_connect():
    wind_obj = Wind(g_logFile, g_writeLogLock)

def test_get_industry_data():
    wind_obj = Wind()
    date = 20171031
    result = wind_obj.get_industry_data(date)
    print (result[0])

def exec_str():
    w.start()

    # data_type = 'daily'
    data_type = "quarter"
    # data_type = 'month'

    allparams_str = "dividendyield2,gr_ttm,profit_ttm,netprofit_ttm,deductedprofit_ttm, \
                        profitnotice_style, profitnotice_date,profitnotice_change,profitnotice_lasteps,\
                        performanceexpress_date,performanceexpress_perfexincome,performanceexpress_perfexprofit,\
                        performanceexpress_perfextotalprofit,performanceexpress_perfexnetprofittoshareholder,performanceexpress_perfexepsdiluted,\
                        performanceexpress_perfexroediluted,performanceexpress_perfextotalassets,performanceexpress_perfexnetassets,\
                        eps_basic,grps,roe_avg,yoyeps_basic,yoy_tr,yoy_or,yoyop,yoyebt,yoyprofit,yoynetprofit,yoynetprofit_deducted,yoy_equity,yoy_assets,\
                        div_cashandstock,div_recorddate,div_exdate,div_paydate,div_prelandate,div_smtgdate,div_impdate"

    quarter_paramsstr = "profitnotice_style, profitnotice_date,profitnotice_change,profitnotice_lasteps,\
                        performanceexpress_date,performanceexpress_perfexincome,performanceexpress_perfexprofit,\
                        performanceexpress_perfextotalprofit,performanceexpress_perfexnetprofittoshareholder,performanceexpress_perfexepsdiluted,\
                        performanceexpress_perfexroediluted,performanceexpress_perfextotalassets,performanceexpress_perfexnetassets,\
                        eps_basic,grps,roe_avg,yoyeps_basic,yoy_tr,yoy_or,yoyop,yoyebt,yoyprofit,yoynetprofit,yoynetprofit_deducted,yoy_equity,yoy_assets,\
                        div_cashandstock,div_recorddate,div_exdate,div_paydate,div_prelandate,div_smtgdate,div_impdate"

    quarter_datestr = "unit=1;currencyType=;Period=Q;Days=Alldays;Fill=Previous"

    daily_paramsstr = "ev,pe_ttm,val_pe_deducted_ttm,pb_lf,dividendyield2, gr_ttm, profit_ttm, netprofit_ttm, deductedprofit_ttm"
    daily_datestr = "unit=1;currencyType=;Days=Alldays;Fill=Previous"

    if data_type == 'daily':
        params_str = daily_paramsstr
        date_str =  daily_datestr
        start_date = "2017-10-31"
        end_date = "2017-10-31"        

    if data_type == 'quarter':
        params_str = quarter_paramsstr
        date_str =  quarter_datestr  
        start_date = "20161030"
        end_date = "20161231"              

    result = w.wsd("600000.SH", params_str, start_date, end_date, date_str)
    print (result.Data)

    w.close()
    
def getSnapData(windObj, secodelist):
    windObj.get_snapshoot_data(secodelist)

    # timer = threading.Timer(timeInterval, getSnapData, [windObj, secodelist])
    # timer.start();

def test_get_snapshoot_data():
    windObj = Wind()
    secodelist = ["000001.SZ", "000002.SZ"]
    
    global timeInterval
    timeInterval = 2.0
    timer = threading.Timer(timeInterval, getSnapData, [windObj, secodelist])
    timer.start();

def test_checkdata():
    dbname = "MarketData_RealTime"
    dbhost = "localhost"

    database_obj = MarketRealTimeDatabase(db=dbname, host=dbhost)    
    result = database_obj.check_data("股票", "000001.SZ", "000001.SZ")
    if result:
        update_data = ['20180101', "151501", "18", "18", "19000000", "000001.SZ"]
        table_name = "000001.SZ"
        database_obj.update_data(update_data, table_name)

def test_get_preclose_data():
    windObj = Wind()
    secode_list = ["000001.SZ", "000002.SZ"]
    result = windObj.get_preclose_data(secode_list)

    dbname = "MarketData_RealTime"
    dbhost = "localhost"
    table_name = "PreCloseData"

    databaseobj = MarketPreCloseDatabase(host=dbhost, db=dbname)
    databaseobj.completeDatabaseTable([table_name])

    colname = "股票"
    update_numb = 0
    insert_numb = 0
    for secode in secode_list:
        if databaseobj.check_data(colname, secode, table_name):            
            if len(result[secode]) == 2: 
                update_numb += 1
                databaseobj.update_data(result[secode], table_name)
        else:
            if len(result[secode]) == 2: 
                insert_numb += 1            
                databaseobj.insert_data(result[secode], table_name)

    print ("update_numb: ", update_numb)
    print ("insert_numb: ", insert_numb) 

def test_getSecodelist():
    windObj = Wind()
    windObj.get_secodelist()

def test_get_index_histdata():
    windObj = Wind()
    # secode = "000951.SH"
    secode = "000001.SZ"
    startdate = "2009-10-1"
    enddate = "2009-11-1"
    keyvalue_list = ["open", "close", "high", "low", "volume", "amt", "pre_close"]
    result = windObj.get_histdata(secode, keyvalue_list, startdate, enddate, "15m")
    print (result)

if __name__ == "__main__":
    # test_connect()
    # test_getSecodeInfo()
    # test_multi_thread_connect()
    # test_get_stockdata()
    # test_get_industry_data()
    # exec_str()
    # test_get_snapshoot_data()
    # test_checkdata()
    # test_get_preclose_data()
    # test_getSecodelist()
    test_get_index_histdata()

