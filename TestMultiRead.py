# -*- coding: UTF-8 -*-
import pickle
from QtAPI import *
from QtDataAPI import *
from TestApi import TestApi
import threading

def loginLogoutFunc(threadName):
    print "***** threadName: %s ***** \n"%(threadName)
    testObj = TestApi()
    qt_usr = "xgzc_api"
    qt_pwd = "UXLAS4YF"
    testObj.QtLogin(qt_usr, qt_pwd)
    testObj.QtLogout(qt_usr)    

def testMultiLoginLogout():
    threadCount = 4
    threads = []
    for i in range(0, threadCount):
        threads.append(threading.Thread(target=loginLogoutFunc, args=(str(i))))
    
    for thread in threads:
        thread.setDaemon(True)
        thread.start()
    thread.join()

def readDataFunc(threadName):
    print "***** threadName: %s ***** \n"%(threadName)
    ret, errMsg, dataCols = GetExchanges("CHN")
    if ret == 0:
        print "[i] ThreadName = %s, GetExchanges Success! Rows = %d \n"%(threading.currentThread().getName(), len(dataCols))
    else:
        print "[x] GetExchanges(", hex(ret), "): ", errMsg    

'''
功能：测试多线程同时读取数据
结果：可以多线程同时读取数据;
'''
def testMultiReadData():
    threadCount = 4
    threads = []

    testObj = TestApi()
    qt_usr = "xgzc_api"
    qt_pwd = "UXLAS4YF"
    testObj.QtLogin(qt_usr, qt_pwd)
      

    for i in range(0, threadCount):
        threads.append(threading.Thread(target=readDataFunc, args=(str(i))))
    
    for thread in threads:
        thread.setDaemon(True)
        thread.start()
    thread.join()    

    testObj.QtLogout(qt_usr)  

def main():
    # testMultiLoginLogout()
    testMultiReadData()

if __name__ == "__main__":
    main()
