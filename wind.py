# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math

from WindPy import *
from CONFIG import *
from func_tool import *
from func_secode import *

class Wind(object):
    def __init__(self,):
        self.__name__ = "Wind"
        self.wind = w
        self.startconnect()

    def __del__(self):
        self.closeconnect()

    def startconnect(self):
        self.wind.start()
        # print 'wind_start_connect'

    def closeconnect(self):
        self.wind.close()
        # print 'wind_close_connect'

    def get_allstock_secode(self):
        all_stockid =self.wind.wset("SectorConstituent","sectorId=a001010100000000;field=wind_code");
        if all_stockid.ErrorCode != 0:
            exception_info = "Get Data failed! exit!"
            raise(Exception(exception_info))
        return  all_stockid.Data[0]

    def get_industry_data(self, date):
        stockid_array = self.get_allstock_secode()
        tmp_result = self.wind.wsd(stockid_array, "industry_gics", str(date), str(date), "industryType=9;Days=Alldays")
        tmp_data = tmp_result.Data[0]
        result = []
        print("tmp_data.size: %d, stockid_array.size: %d" %(len(tmp_data), len(stockid_array)))
        for i in range(len(stockid_array)):
            secode = stockid_array[i][7:9] + stockid_array[i][0:6]
            try:
                if tmp_data[i] == None or '--' not in tmp_data[i]:
                    industry_array = [" ", " ", " ", " "]
                    print (secode, tmp_data[i])
                else:
                    industry_array = tmp_data[i].split('--')
            except Exception as e:
                print (i) 
                print (secode) 
                print (tmp_data[i])
                raise(e)
            
            # print industry_array
            result.append([secode])
            result[i].extend(industry_array)
        return result

    def get_snapshoot_data(self, secodelist):
        # print "get_snapshoot_data: ", secodelist
        result = {}
        for secode in secodelist:
            result[secode] = []
        # print result

        indicators = "rt_date,rt_time,rt_latest,rt_pre_close,rt_amt"
        tmp = self.wind.wsq(secodelist, indicators)
        # print tmp

        if tmp.ErrorCode == 0:
            tmp_data = tmp.Data
            # print tmp_data
            for i in range(len(tmp_data)):
                for j in range(len(secodelist)):
                    # print tmp_data[i][j]
                    result[secodelist[j]].append(tmp_data[i][j])

            wsqTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            for secode in secodelist:
                result[secode].append(secode)
                result[secode].append(str(wsqTime))
            # print result
            return result
        else:
            # print tmp.ErrorCode
            raise(Exception("Get SnapShoot Data Failed , ErroCode is: " + str(tmp.ErrorCode)))

    def get_preclose_data(self, secodelist):
        # print "get_snapshoot_data: ", secodelist
        result = {}
        for secode in secodelist:
            result[secode] = []
        print ("len(result): ", len(result))

        indicators = "pre_close"
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        options = "Days=Alldays"
        tmp = self.wind.wsd(secodelist, indicators, date, date, options)
        print (tmp)

        if tmp.ErrorCode == 0:
            tmp_data = tmp.Data

            for i in range(len(tmp_data)):
                for j in range(len(secodelist)):
                    # print tmp_data[i][j]
                    result[secodelist[j]].append(tmp_data[i][j])

            for secode in secodelist:
                result[secode].append(secode)

            # print result
            return result        
        else:
            # print tmp.ErrorCode
            raise(Exception("Get PreCLose Data Failed , ErroCode is: " + str(tmp.ErrorCode)))

    def get_restore_historydata(self, startdate, enddate, secode):
        tmp = self.wind.wsd("600000.SH", "close", startdate, enddate, "PriceAdj=F")
        if tmp.ErrorCode == 0:
            result = []
            # print tmp

            for i in range(len(tmp.Times)):
                result.append([])

            for i in range(len(tmp.Times)):
                result[i].append(str(tmp.Times[i]).replace('-', ''))
                result[i].append(float("%.2f " % tmp.Data[0][i]))

            return result    
        else:
            # print tmp.ErrorCode
            raise(Exception("get_restore_historydata Failed , ErroCode is: " + str(tmp.ErrorCode)))

    def get_histdata(self, secode, keyvalue_list, startdate, enddate, time_type = "day"):
        secode = trans_tinycode_to_wind(secode)
        if time_type == "day":
            # print('secode: %s, start_date: %s, end_date: %s' % \
            #      (secode, str(startdate), str(enddate)))
            tmp = self.wind.wsd(secode, keyvalue_list, str(startdate), str(enddate), "PriceAdj=F")
        else:
            # print("time_type: %s" % (time_type))
            start_datetime = str(startdate) + " 09:00:00"
            end_datetime = str(enddate) + " 15:30:00"
            minute_type = time_type[0:len(time_type)-1]
            time_str = "BarSize=%s" %(minute_type)
            # print("startdate: %s, enddate: %s" % (startdate, enddate))
            # print("start_datetime: %s, end_datetime: %s" % (start_datetime, end_datetime))
            # print("time_str: %s " % (time_str) )
            tmp = self.wind.wsi(secode, keyvalue_list, str(start_datetime), str(end_datetime), time_str)
        if tmp.ErrorCode == 0:
            result = []
            for i in range(len(tmp.Times)):
                result.append([])

            for i in range(len(tmp.Times)):
                date_time = str(tmp.Times[i])
                date_time = date_time.replace('-','')
                result[i].append(date_time)
                # print(date_time)
                for j in range(len(keyvalue_list)):
                    result[i].append(float("%.4f " % tmp.Data[j][i]))

            return result    
        else:
            raise(Exception("get_restore_historydata Failed , ErroCode is: %s" %(str(tmp.ErrorCode))))

    def get_secode_compname(self, secode_list):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        result = self.wind.wsd(secode_list, "comp_name", date, date, "")
        data = result.Data[0]        
        return data

    def get_market_secodelist(self, market_name):
        tmp_result =self.wind.wset("SectorConstituent","date=%s;sectorId=%s;field=wind_code,sec_name" \
                                    % (datetime.datetime.now().strftime('%Y-%m-%d'), market_name));
        if tmp_result.ErrorCode != 0:
            exception_info = "Get Data failed! exit!"
            raise(Exception(exception_info))

        result = []
        for i in range(len(tmp_result.Data[0])):
            result.append([pure_secode(tmp_result.Data[0][i]), tmp_result.Data[1][i]])

        return result     

    def get_secodelist(self):
        tmp = self.wind.wset("indexconstituent","date=2018-03-05;windcode=000906.SH")
        print (len(tmp.Data[2]))
        if tmp.ErrorCode == 0:
            result = []
            return result    
        else:
            raise(Exception("get_secodelist Failed , ErroCode is: " + str(tmp.ErrorCode)))

    def get_day_data(self):
        pass

    def get_minute_data(self):        
        pass

class TestWind(object):
    def __init__(self):
        self.__name__ = '__TestWind__'
        self.test_get_histdata()

    def test_get_histdata(self):
        code = "SZ000001"
        start_date = '20070108'
        end_date = '20070118'
        keyvalue_list = ['close']
        wind_obj = Wind()
        result = wind_obj.get_histdata(code, keyvalue_list, start_date, end_date)
        # print(result)


if __name__ == "__main__":
    test_obj = TestWind()