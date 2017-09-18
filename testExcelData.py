# -*- coding: UTF-8 -*-
import time
import pickle
import xlrd
from QtAPI import *
from QtDataAPI import *
from example import MSSQL
from TestApi import TestApi
# from toolFunc import getSimpleDate, getSimpleTime, transExcelTimeToStr, getSecodeInfo, GetSecodeInfo
from toolFunc import *


import os, sys
import traceback

import datetime
import threading

# def deleteRetiredSecodeInfo(secodeInfo, execlFileDirName):
#     excelFileNameArray = os.listdir(execlFileDirName)
#     print 'Secode Numb : %d, Excel File Numb: %d' %(len(secodeInfo), len(excelFileNameArray))

#     i = 0
#     while i < len(secodeInfo):      
#         symbol = str(secodeInfo[i][0])
#         market = str(secodeInfo[i][1])
#         fileName = market + symbol + '.xlsx'    
#         if fileName not in excelFileNameArray:
#             secodeInfo.pop(i)
#             print fileName
#             continue
#         i = i + 1

#     print 'Afte delete Secode Numb : %d' %(len(secodeInfo))
#     return secodeInfo

# def completeDatabaseTable(secodeInfo, execlFileDirName):
#     excelFileNameArray = os.listdir(execlFileDirName)
#     secodeExelFileName = []
#     for i in range (len(secodeInfo)):
#         symbol = str(secodeInfo[i][0])
#         market = str(secodeInfo[i][1])
#         fileName = market + symbol + '.xlsx'            
#         secodeExelFileName.append(fileName)

#     for i in range(len(excelFileNameArray)):        
#         if excelFileNameArray[i] not in secodeExelFileName:            
#             symbol = excelFileNameArray[i][2:8]
#             market = excelFileNameArray[i][0:2]
#             secodeInfo.append([symbol,market])
#             print (symbol,market)
        
def main():
    secodeInfo = GetSecodeInfo()
    execlFileDirName = "E:\DataBase\original-data-20160910-20170910-1m"
    secodeInfo = deleteRetiredSecodeInfo(secodeInfo, execlFileDirName)
    print 'Afte delete Secode Numb : %d' %(len(secodeInfo))

    secodeInfo = AddSecodeInfo(secodeInfo, execlFileDirName)
    print 'Afte add Secode Numb : %d' %(len(secodeInfo))


if __name__ == "__main__":
    main()
    
