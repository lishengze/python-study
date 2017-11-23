# -*- coding: UTF-8 -*-
import time
import os, sys
import traceback
import pyodbc

import datetime

from CONFIG import *
from toolFunc import *

from wind import Wind

from database import Database
from market_database import MarketDatabase
from market_datanet import MarketTinySoft

def compute_dailydata_byminudata(minu_data):
    pass

def get_ori_data(start_date, end_date):
    pass

def get_daytime_array(start_date, end_date):
    pass 

def compare_data(data_type, start_date, end_date):
    netconn_obj = MarketTinySoft(data_type)
    databse_obj = MarketDatabase(data_type)
    tablename_array = databse_obj.getDatabaseTableInfo()
    secode_array = tablename_array

    for secode in secode_array:
        
