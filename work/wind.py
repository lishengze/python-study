# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math

from WindPy import *
from CONFIG import *
from toolFunc import *

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
        tmp_result = self.wind.wsd(stockid_array, "industry_gics", str(date), str(date), "industryType=9")
        tmp_data = tmp_result.Data[0]
        result = []
        for i in range(len(stockid_array)):
            secode = stockid_array[i][7:9] + stockid_array[i][0:6]
            industry_array = tmp_data[i].split('--')
            # print industry_array
            result.append([secode])
            result[i].extend(industry_array)
        return result
