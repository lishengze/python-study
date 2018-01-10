from wind import Wind
from market_database import MarketDatabase
from toolFunc import *

def get_windhist_data():
    windobj = Wind()
    startdate = "2016-04-08"
    enddate = "2018-01-09"
    secode = "600000.SH"
    result = windobj.get_restore_historydata(startdate, enddate, secode)
    print "wind data numb: ", len(result)
    return result

def get_database_histdata():
    # dbhost = "192.168.211.165"
    dbhost = "localhost"
    dbname = "MarketData_day"
    markdata_obj = MarketDatabase(host=dbhost, db=dbname)
    secode = "SH600000"
    startdate = "20160408"
    enddate = "20180109"
    result = markdata_obj.get_histdata_bytime(startdate, enddate, secode)
    print "database data numb: ", len(result)
    trans_result = []
    for i in range(len(result)):
        tmpdata = []
        tmpdata.append(str(result[i][0]))
        tmpdata.append(float("%.2f " % result[i][4]))
        tmpdata.append(float(result[i][9]))
        trans_result.append(tmpdata)
    return trans_result

def compare_date(wind_data, database_data):
    wind_datelist = []
    database_datelist = []

    for i in range(len(wind_data)):
        wind_datelist.append(wind_data[i][0])

    for i in range(len(database_data)):
        database_datelist.append(str(database_data[i][0]))

    wind_unique_date = []
    database_unique_date = []

    for date in wind_datelist:
        if date not in database_datelist:
            wind_unique_date.append(date)

    for date in database_datelist:
        if date not in wind_datelist:
            database_unique_date.append(date)

    print "database_unique_date: ", database_unique_date
    print "wind_unique_date: ", wind_unique_date 

def compute_restore_data(database_data):
    restore_data = []
    for i in range(len(database_data)):
        restore_data.append([])

    latest_data = float(database_data[len(database_data)-1][1])
    i = len(database_data) - 1
    # print i
    while i > -1:     
        index = len(database_data) - 1 - i 
        # print "index: ", index
        restore_data[index].append(str(database_data[i][0]))
        restore_data[index].append(float("%.2f " % latest_data))
        latest_data = latest_data / (1 + float(database_data[i][2]))
        i = i-1
    restore_data.reverse()
    # print_data("restore_data: ", restore_data)
    return restore_data

def compare_database_ori_restore_data(oridata, restore_data):
    differ_list = []
    for i in range(len(oridata)):
        if oridata[i][0] == restore_data[i][0] and oridata[i][1] != restore_data[i][1]:
            differ_list.append([oridata[i][0], restore_data[i][1], oridata[i][1]])
    print_data("compare_database_ori_restore_data: ", differ_list)
    return differ_list

def compare_oridata(wind_data, database_data):
    differ_list = []
    for i in range(len(database_data)):
        # print wind_data[i][0], wind_data[i][1], database_data[i][0], database_data[i][1]
        if wind_data[i][0] == database_data[i][0] and wind_data[i][1] != float("%.2f " % database_data[i][1]):
           tmpdata = [wind_data[i][0], wind_data[i][1], database_data[i][1]]
        #    print tmpdata
           differ_list.append(tmpdata)
    print_data("compare_oridata: ", differ_list)
    return differ_list

def compare_restoredata(wind_restoredata, database_restoredata):
    differ_list = []
    for i in range(len(database_restoredata)):
        # print wind_restoredata[i], database_restoredata[i]
        if wind_restoredata[i][0] == database_restoredata[i][0] and \
           wind_restoredata[i][1] != database_restoredata[i][1]:
           tmpdata = [wind_restoredata[i][0], wind_restoredata[i][1], database_restoredata[i][1]]
           differ_list.append(tmpdata)
    print_data("compare_restoredata: ", differ_list)
    return differ_list

def main():
    wind_data = get_windhist_data()
    database_data = get_database_histdata()
    compare_date(wind_data, database_data)
    database_restoredata = compute_restore_data(database_data)
    compare_database_ori_restore_data(database_data, database_restoredata)
    compare_oridata(wind_data, database_data)
    compare_restoredata(wind_data, database_restoredata)
    

if __name__ == "__main__":
    main()