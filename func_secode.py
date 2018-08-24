import math

import os
import traceback
import threading
import pyodbc
import datetime
import math
from operator import itemgetter, attrgetter
import time
import datetime
import threading

from excel import EXCEL

from CONFIG import *
from func_time import *
from func_tool import *

def get_execl_code(filename):
    excelObj = EXCEL()
    secodeList = excelObj.get_data_byindex(filename, 0)
    return secodeList

def complete_excel_code(oricode):
    complete_code = str(oricode)
    while len(complete_code) < 6:
        complete_code = '0' + complete_code
    return complete_code

def trans_code_to_windstyle(oricode):
    wind_code = str(oricode)
    while len(wind_code) < 6:
        wind_code = '0' + wind_code

    if wind_code.startswith('6'):
        wind_code += '.SH'
    else:
        wind_code += '.SZ'
    return wind_code

def trans_tinycode_to_wind(oricode):
    result = oricode
    if result.startswith("SH"):
        result = result[2:len(result)]
        result += '.SH'
    if result.startswith("SZ"):
        result = result[2:len(result)]
        result += '.SZ'

    # print ("result: ", result)
    return result

def get_indexcode(style="ori"):
    indexCodeArray = []
    if style == "wind":
        indexCodeArray = ["000300.SH", "000016.SH", "000852.SH", \
                          "000904.SH", "000905.SH", "000906.SH", "399903.SZ"]
                          
    if style == "tinysoft":
        indexCodeArray = ["SH000300", "SH000016", "SH000852", \
                          "SH000904", "SH000905", "SH000906", "SZ399903"]
                        
    if style == "ori":
        indexCodeArray = ["000300", "000016", "000852", \
                          "000904", "000905", "000906", "399903"]
    return indexCodeArray

def get_all_indexcode(style="ori"):
    indexCodeArray = []
    if style == "wind":
        indexCodeArray = ["000300.SH", "000016.SH", "000852.SH", \
                          "000904.SH", "000905.SH", "000906.SH", "399903.SZ", \
                          '000908.SH', '000909.SH', '000910.SH', '000911.SH', \
                          '000912.SH', '000913.SH', '000914.SH', '000915.SH', '000917.SH',\
                          '000951.SH', '000849.SH', '000952.SH']
                          
    if style == "tinysoft":
        indexCodeArray = ["SH000001", "SH000002", "SH000003", "SH000010", "SH000009",\
                          "SZ399001", "SZ399006", "SZ399005", "SZ399008", "SZ399102", "SZ399673", \
                          "SZ399101", "SZ399102", "SZ399106",  "SZ399107", "SZ399108", \
                          "SH000300", "SH000016", "SH000852", \
                          "SH000904", "SH000905", "SH000906", "SZ399903", \
                          'SH000908', 'SH000909', 'SH000910', 'SH000911', \
                          'SH000912', 'SH000913', 'SH000951', 'SH000849', \
                          'SH000952', 'SH000915', 'SH000917']
                        
    if style == "ori":
        indexCodeArray = ["000300", "000016", "000852", \
                          "000904", "000905", "000906", "399903", \
                          '000908', '000909', '000910', '000911', \
                          '000912', '000913', '000951', '000849', \
                          '000952', '000915', '000917']
    return indexCodeArray

def get_secode_list_from_excel(fileName, style='ori'):    
    execlObj = EXCEL()
    ori_data = execlObj.get_alldata_bysheet(fileName)
    secode_list = []
    index = 1
    while index < len(ori_data):
        secode_list.append(getCompleteSecode(ori_data[index][0], style=style))
        index += 1
    return secode_list

def getCompleteSecode(oricode, style="ori"):
    complete_code = str(oricode)
    if len(complete_code) > 6:
        return complete_code

    while len(complete_code) < 6:
        complete_code = '0' + complete_code

    if style == "tinysoft":
        if complete_code.startswith("6"):
            complete_code = "SH" + complete_code
        else:
            complete_code = "SZ" + complete_code
    
    if style == "wind":
        if complete_code.startswith("6"):
            complete_code = complete_code + ".SH"
        else:
            complete_code = complete_code + ".SZ"

    return complete_code
  
def get_excel_secode(dirname):
    secodelist = []
    filename_array = get_filename_array(dirname)    
    newFileIn = False
    for filename in filename_array:
        complete_filename = dirname + '/' + filename
        excelobj = EXCEL()
        tmp_secodelist = excelobj.get_data_byindex(complete_filename)
        for code in tmp_secodelist:
            complete_code = complete_excel_code(code)
            if complete_code not in secodelist:
                secodelist.append(complete_code)      
    return secodelist

def pure_secode(secode):
    if len(secode) < 7:
        return secode
    
    if len(secode) == 8:
        secode = secode[2:8]

    if len(secode) == 9:
        secode = secode[0:6]

    return secode
