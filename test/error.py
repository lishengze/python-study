import threading
import pyodbc
import traceback

def simpleConnect():
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        curs.close()
        conn.close()

        infoStr = "[i] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "SimpleConnect Succeed \n"
        print infoStr
        
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "SimpleConnect Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr


def testMultiThreadConnect():
    try:
        thread_count = 2
        threads = []

        for i in range(thread_count):
            tmpThread = threading.Thread(target=simpleConnect)
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                + "TestMultiThread Failed" + "\n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr 

if __name__ == "__main__":
    testMultiThreadConnect()        