from wind import Wind
from market_database import MarketDatabase

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
    return result

def compare_date(wind_data, database_data):
    wind_datelist = []
    database_datelist = []

    for i in range(len(wind_data)):
        wind_datelist.append(str(wind_data[i][0]).replace('-', ''))

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

    latest_data = float(database_data[len(database_data)-1][4])
    i = len(database_data) - 1
    # print i
    while i > -1:     
        index = len(database_data) - 1 - i 
        # print "index: ", index
        restore_data[index].append(str(database_data[i][0]))
        restore_data[index].append(float("%.2f " % latest_data))
        latest_data = latest_data / (1 + float(database_data[i][9]))
        i = i-1
    restore_data.reverse()
    print restore_data
    return restore_data


def main():
    wind_data = get_windhist_data()
    database_data = get_database_histdata()
    compare_date(wind_data, database_data)
    compute_restore_data(database_data)

if __name__ == "__main__":
    main()