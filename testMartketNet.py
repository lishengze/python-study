# -*- coding: UTF-8 -*-
import time

import os, sys
import traceback
import pyodbc

import datetime
import threading
import multiprocessing 

from CONFIG import *
from func_tool import *

from market_database import MarketDatabase
from market_datanet import MarketTinySoft

def test_getHsl():
    datatype = "MarketData_day"
    netconnct_obj = MarketTinySoft(datatype=datatype)
    secode = "SH600000"
    startdate = 20180311
    enddate = 20180316
    # result = netconnct_obj.get_HSL(secode, startdate, enddate)
    result = netconnct_obj.get_HSL_upgrade(secode, startdate, enddate)
    print result

def test_getNetData():
    datatype = "MarketData_day"
    netconnct_obj = MarketTinySoft(datatype=datatype)
    secode = "SH600000"
    startdate = 20180320
    enddate = 20180320

    result = netconnct_obj.get_netdata([secode, startdate, enddate])
    print_data("Added result: ", result)

    # result = netconnct_obj.get_Volume(secode, startdate, enddate)
    # print result

if __name__ == "__main__":
    # test_getHsl()
    test_getNetData()