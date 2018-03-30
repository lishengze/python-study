# -*- coding: UTF-8 -*-
import time

import os, sys
import traceback
import pyodbc

import datetime
import threading
import multiprocessing 

from CONFIG import *
from toolFunc import *

from database import Database
from excel import EXCEL

from market_database import MarketDatabase
from market_datanet import MarketTinySoft


def testGetTurnoverData():
    datatype = "MarketData_day"
    host = "192.168.211.165"
    databaseObj = MarketDatabase(db=datatype, host=host)
    secode = "SH600000"
    result = databaseObj.get_data_turnover(secode)
    print_list("turnover data: ", result)

def getOriSecodeList(fileName):    
    execlObj = EXCEL()
    secodeList = execlObj.get_data_bysheet(fileName)
    return secodeList

def transSecodeList(oriSecodeList, style="tinysoft"):
    result = []
    for i in range(len(oriSecodeList)):
        result.append(getCompleteSecode(oriSecodeList[i], style="tinysoft"))
    return result

def get_turnover_list(oridata):
    result = []
    for i in range(len(oridata)):
        result.append(oridata[i][2])
    return result

def get_close_list(oridata):
    result = []
    for i in range(len(oridata)):
        result.append(oridata[i][3])
    return result

def get_time_list(oridata):
    result = []
    for i in range(len(oridata)):
        item = oridata[i]
        result.append([item[0], item[1]])
    return result

def trans_time_list(oridata):
    result = []
    for i in range(len(oridata)):
        item = oridata[i]
        result.append(str(item[0]) + " " + str(item[1]))
    return result

def completeResult(oriResult, indexTimeArray):
    result_time_list = get_time_list(oriResult)
    missed_time = []
    delist_data = []
    on_market = False
    curr_result_item = oriResult[0]
    for i in range(len(indexTimeArray)):
        item = indexTimeArray[i]
        if item not in result_time_list:
            if True == on_market:
                oriResult.append([item[0], item[1], 0, curr_result_item[3]])
                delist_data.append([item[0], item[1], 0, curr_result_item[3]])
            else:
                oriResult.append([item[0], item[1], -1, -1])
                missed_time.append([item[0], item[1]])             
        else:
            on_market = True
            curr_result_item = oriResult[result_time_list.index(item)]
    oriResult.sort(key=itemgetter(0,1))

    i = 0
    delete_data = []
    while i < len(oriResult):
        if [oriResult[i][0], oriResult[i][1]] not in indexTimeArray:
            delete_data.append(oriResult[i])
            oriResult.remove(oriResult[i])
            i = i - 1
        i = i + 1

    # print_list("delete_data: ", delete_data)
    # print_list("missed_time: ", missed_time)
    
    return oriResult, delete_data, missed_time, delist_data

def clearSecodeList(oriSecodeList, databaseObj):
    table_list = databaseObj.getDatabaseTableInfo()
    cleared_secode_list = []
    for secode in oriSecodeList:
        if getCompleteSecode(secode, "tinysoft") not in table_list:
            # oriSecodeList.remove(secode)
            cleared_secode_list.append(secode)
    return cleared_secode_list

def test_sort():
    oridata = [[2018, 1500, 17], [2018, 1300, 8], [2017, 1800, 1], [2017, 20000,15]]
    print oridata 
    oridata.sort(key=itemgetter(0,1))
    print oridata

def main():
    # time_type = "day"
    time_type = "10m"
    datatype = "MarketData_" + time_type
    host = "192.168.211.165"
    fileName = u"D:\strategy\Real\沪深300成分股代码.xlsx"
    des_file_name = u"D:\strategy\\MarketData_" + time_type + ".xlsx"
    key_list = ["TDATE", "TIME", "TURNOVER", "TCLOSE"]
    databaseObj = MarketDatabase(db=datatype, host=host)
    execlObj = EXCEL()
    oriSecodeList = getOriSecodeList(fileName)
    indexcode = "SH000300"
    oriSecodeList.append(indexcode)

    cleared_secode_list = clearSecodeList(oriSecodeList, databaseObj)
    # print_list("cleared_secode_list: ", cleared_secode_list)
    # print_list("all_secodeList: ", oriSecodeList, len(oriSecodeList))
        
    index_time_list = get_time_list(databaseObj.get_data_bykey(key_list, indexcode))
    index_str_time_list = trans_time_list(index_time_list)
    index_str_time_list.insert(0, "time\\code")
        
    # colIndex = 0
    # execlObj.write_single_column_data(index_str_time_list, des_file_name, colIndex, "turnover")
    # execlObj.write_single_column_data(index_str_time_list, des_file_name, colIndex, "close")
    # colIndex += 1

    b_single_write = True

    # oriSecodeList = oriSecodeList[0:6]

    if b_single_write:    
        all_turnover_list = []
        all_close_list = []
        print "------- Start Read Data -------"
        readdata_starttime = datetime.datetime.now()
        index = 0
        key_value_list = ["turnover"]
        # key_value_list = ["close"]
        for key_value in key_value_list:
            sheet_name = key_value
            colIndex = 0
            execlObj.write_single_column_data(index_str_time_list, des_file_name, colIndex, sheet_name)
            for secode in oriSecodeList:
                curr_turnover_list = []
                curr_close_list = []

                if secode in cleared_secode_list:
                    tmpdata = []
                    for i in range(len(index_time_list)):
                        curr_turnover_list.append(-1)
                        curr_close_list.append(-1)                
                else:
                    ori_result = databaseObj.get_data_bykey(key_list, getCompleteSecode(secode, "tinysoft"))
                    comp_result, delete_data, missed_time, delist_data = completeResult(ori_result, index_time_list)
                    if key_value == "turnover":
                        curr_turnover_list = get_turnover_list(comp_result)

                    if key_value == "close":
                        curr_close_list = get_close_list(comp_result)

                if key_value == "turnover" and secode != indexcode:
                    curr_turnover_list.insert(0, secode)
                    all_turnover_list.append(curr_turnover_list)

                if key_value == "close":
                    if secode == indexcode:
                        secode = pure_secode(secode)

                    curr_close_list.insert(0, secode)            
                    all_close_list.append(curr_close_list)

                print "secode: ", secode, ", turnover numb: ", len(curr_turnover_list), ", close numb: ", len(curr_close_list), \
                    ", delete numb: ", len(delete_data), ", delist numb: ", len(delist_data), ", unlist numb: " , len(missed_time), \
                    ", index: ", index

                if len(delist_data) != 0:
                    print "delist data: ", delist_data

                if len(delete_data) != 0:
                    print "delete data: ", delete_data            

                index += 1

            readdata_endtime = datetime.datetime.now()
            print "------- Read data end , cost: ", (readdata_endtime - readdata_starttime).total_seconds(), "s -------"

            print "------- Start write Data -------"

            if key_value == "turnover":
                execlObj.write_all_data(all_turnover_list, des_file_name, "turnover")
                all_turnover_list = []

            if key_value == "close":
                execlObj.write_all_data(all_close_list, des_file_name, "close")
                all_close_list = []

            writedata_endtime = datetime.datetime.now()
            print "------- Write data end , cost: ", (writedata_endtime - readdata_endtime).total_seconds(), "s -------"
    else:
        all_turnover_list = []
        all_close_list = []
        print "------- Start Read Data -------"
        readdata_starttime = datetime.datetime.now()
        index = 0
        for secode in oriSecodeList:
            curr_turnover_list = []
            curr_close_list = []

            if secode in cleared_secode_list:
                tmpdata = []
                for i in range(len(index_time_list)):
                    curr_turnover_list.append(-1)
                    curr_close_list.append(-1)                
            else:
                ori_result = databaseObj.get_data_bykey(key_list, getCompleteSecode(secode, "tinysoft"))
                comp_result, delete_data, missed_time, delist_data = completeResult(ori_result, index_time_list)
                curr_turnover_list = get_turnover_list(comp_result)
                curr_close_list = get_close_list(comp_result)

            if secode != indexcode:
                curr_turnover_list.insert(0, secode)
                all_turnover_list.append(curr_turnover_list)

            if secode == indexcode:
                secode = pure_secode(secode)

            curr_close_list.insert(0, secode)            
            all_close_list.append(curr_close_list)

            print "secode: ", secode, ", turnover numb: ", len(curr_turnover_list), ", close numb: ", len(curr_close_list), \
                  ", delete numb: ", len(delete_data), ", delist numb: ", len(delist_data), ", unlist numb: " , len(missed_time), \
                  ", index: ", index

            if len(delist_data) != 0:
                print "delist data: ", delist_data

            if len(delete_data) != 0:
                print "delete data: ", delete_data            

            index += 1

        readdata_endtime = datetime.datetime.now()
        print "------- Read data end , cost: ", (readdata_endtime - readdata_starttime).total_seconds(), "s -------"

        print "------- Start write Data -------"

        execlObj.write_all_data(all_turnover_list, des_file_name, "turnover")
        all_turnover_list = []

        execlObj.write_all_data(all_close_list, des_file_name, "close")
        all_close_list = []

        writedata_endtime = datetime.datetime.now()
        print "------- Write data end , cost: ", (writedata_endtime - readdata_endtime).total_seconds(), "s -------"
            
def test_deal_turonver_data():
    datatype = "MarketData_day"
    host = "192.168.211.165"
    fileName = u"D:\strategy\Real\沪深300成分股代码.xlsx"
    des_file_name = u"D:\strategy\\test_write.xlsx"
    databaseObj = MarketDatabase(db=datatype, host=host)
    execlObj = EXCEL()

    indexcode = "SH000300"
    index_time_list= get_time_list(databaseObj.get_data_turnover(indexcode))
    index_str_time_list = trans_time_list(index_time_list)
    index_str_time_list.insert(0, "time\\code")
    # print_list("index_time_list: ", index_time_list)
    # print_list("index_str_time_list: ", index_str_time_list)

    colIndex = 0
    execlObj.write_single_column_data(index_str_time_list, des_file_name, colIndex)

    result = [[20180328, 140000, 1], [20140327, 150000, 9], \
              [20140217, 150000, 8], [20131129, 150000, 15]]

    result = completeResult(result, index_time_list)
    result = get_turnover_list(result)
    result.insert(0, "Test")
    # print_list("transResult: ", result)
    colIndex += 1
    execlObj.write_single_column_data(result, des_file_name, colIndex)                 

def test_write_data():
    oridata = range(3)
    execlObj = EXCEL()
    des_file_name = u"D:\strategy\\test_write.xlsx"

    colindex = 0
    for value in oridata:
        execlObj.write_single_column_data([value], des_file_name, colindex, "test")
        colindex += 1
    
if __name__ == "__main__":
    # testGetTurnoverData()
    main()
    # test_sort()
    # test_deal_turonver_data()
    # test_write_data()