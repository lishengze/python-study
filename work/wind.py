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
        self.conn = w
        self.start_connect()

    def __del__(self):
        self.close_connect()

    def start_connect(self):
        self.conn.start()
        # print 'wind_start_connect'

    def close_connect(self):
        self.conn.close()
        # print 'wind_close_connect'

    def get_allA_secode(self):
        AllAStock =self.conn.wset("SectorConstituent","sectorId=a001010100000000;field=wind_code");
        if AllAStock.ErrorCode != 0:
            exception_info = "Get Data failed! exit!"
            raise(Exception(exception_info))
        return AllAStock.Data[0]

    def get_industry_data(self, date):
        stockId_array = self.get_allA_secode()
        tmp_result = self.conn.wsd(stockId_array, "industry_gics", str(date), str(date), "industryType=9")
        tmp_data = tmp_result.Data[0]
        result = []
        for i in range(len(stockId_array)):            
            secode = stockId_array[i][7:9] + stockId_array[i][0:6]
            industry_array = tmp_data[i].split('--')
            # print industry_array
            result.append([secode])
            result[i].extend(industry_array)
        return result
