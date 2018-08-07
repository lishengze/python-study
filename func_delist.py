from func_tool import *

def get_market_susdata_bg(added_datetime, secode, close_price):
    appenddata = []
    appenddata.append(added_datetime[0])
    appenddata.append(added_datetime[1])
    appenddata.append(secode)
    appenddata.append(close_price)
    appenddata.append(close_price)
    appenddata.append(close_price)
    appenddata.append(close_price)
    appenddata.append(0)
    appenddata.append(0)
    appenddata.append(0)
    appenddata.append(close_price)
    appenddata.append(0)
    appenddata.append(1)
    appenddata.append(1)
    appenddata.append(1)
    return appenddata

def get_market_susdata(added_datetime, susdata):
    appenddata = []
    appenddata.append(added_datetime[0])
    appenddata.append(added_datetime[1])
    appenddata.append(susdata[2])
    appenddata.append(susdata[3])
    appenddata.append(susdata[4])
    appenddata.append(susdata[5])
    appenddata.append(susdata[6])
    appenddata.append(0)
    appenddata.append(0)
    appenddata.append(0)
    appenddata.append(susdata[4])
    appenddata.append(0)
    appenddata.append(susdata[12])
    appenddata.append(susdata[13])
    appenddata.append(susdata[14])
    return appenddata

def get_tradetime_startindex(tradetime_array, ori_netdata, isLeftInterval):
    tradetime_index = 0
    if isLeftInterval :
        if len(ori_netdata) == 0 or (len(ori_netdata) == 1 and is_minute_data(ori_netdata[0][1])):
            return -1
        else:
            i = 0
            while i < len(tradetime_array):
                item = tradetime_array[i]
                if is_time_equal(item, [int(ori_netdata[0][0]), int(ori_netdata[0][1])]):
                    tradetime_index = i
                    break  
                i += 1
    return tradetime_index

def is_trade_time_late(tradetime, netdatatime):
    cur_oridatetime = [int(netdatatime[0]), int(netdatatime[1])]
    cur_tradetime = tradetime
    return is_time_late(cur_tradetime, cur_oridatetime)

def com_delist_data(tradetime_array, ori_netdata, isLeftInterval=False, latest_data=[]):
    complete_data = []
    tradetime_index = get_tradetime_startindex(tradetime_array, ori_netdata, isLeftInterval)
    oridata_index = 0
    add_count = 0
    tmp_tradetime_index = tradetime_index

    while tradetime_index < len(tradetime_array):
        if oridata_index == len(ori_netdata) or \
            is_trade_time_late(tradetime_array[tradetime_index], ori_netdata[oridata_index]):

            added_datetime = tradetime_array[tradetime_index]
            if oridata_index == 0:
                if len(latest_data) != 0:
                    susdata = latest_data
                    # secode = latest_data[2]
                    # open_price = latest_data[3]
                    # close_price = latest_data[4]
                    # high_price = latest_data[5]
                    # low_price = latest_data[6]
                else:
                    break                 
            else:
                susdata = ori_netdata[oridata_index-1]
                # secode = ori_netdata[oridata_index-1][2]
                # close_price = ori_netdata[oridata_index-1][4]
            appenddata = get_market_susdata(added_datetime, susdata)
            ori_netdata.insert(oridata_index, appenddata)
            add_count += 1

        oridata_index = oridata_index + 1
        tradetime_index = tradetime_index + 1
    
    # print ('tradetime_index: %d, tradetime_array.size: %d, ori_netdata.size: %d, add_count: %d' %\
    #         (tmp_tradetime_index, len(tradetime_array), len(ori_netdata), add_count) )

    # print ("end tradetime_index %d, end oridata_index %d" % 
    #         (tradetime_index, oridata_index))

    # print "End: tradetime_index: ", tradetime_index, ", oridata_index: ", oridata_index
    # while tradetime_index < len(tradetime_array):
    #     added_datetime = tradetime_array[tradetime_index]
    #     secode = ""
    #     close_price = 0
    #     if oridata_index == 0:
    #         secode = latest_data[2]
    #         close_price = latest_data[4]
    #     else:
    #         secode = ori_netdata[oridata_index-1][2]
    #         close_price = ori_netdata[oridata_index-1][4]
    #     appenddata = get_market_susdata(added_datetime, secode, close_price)
    #     ori_netdata.insert(oridata_index, appenddata)

    #     tradetime_index += 1
    #     oridata_index += 1
    #     add_count += 1

    # print "add_count: ", add_count    
    complete_data = ori_netdata
    return complete_data
    
def com_delist_data_bg(tradetime_array, ori_netdata, isLeftInterval=False):
    complete_data = []
    tradetime_index = get_tradetime_startindex(tradetime_array, ori_netdata, isLeftInterval)
    oridata_index = 0
    add_count = 0

    if tradetime_index == -1:
        return []

    while tradetime_index < len(tradetime_array):
        if oridata_index == len(ori_netdata) or \
            is_trade_time_late(tradetime_array[tradetime_index], ori_netdata[oridata_index]):

            added_datetime = tradetime_array[tradetime_index]
            secode = ori_netdata[oridata_index-1][2]
            close_price = ori_netdata[oridata_index-1][4]
            
            appenddata = get_market_susdata(added_datetime, secode, close_price)
            ori_netdata.insert(oridata_index, appenddata)
            add_count += 1

        oridata_index = oridata_index + 1
        tradetime_index = tradetime_index + 1 
    complete_data = ori_netdata
    return complete_data

def append_database_data(ori_netdata, isLeftInterval, first_data=[]):
    is_append_first_data = False
    if isLeftInterval == True and first_data != []:
        index = len(ori_netdata) - 1
        while index >= 0 and not is_time_early( [int(first_data[0]), int(first_data[1])],\
                                                [int(ori_netdata[index][0]), int(ori_netdata[index][1])]):
            ori_netdata.remove(ori_netdata[index])
            index -= 1
        ori_netdata.append(first_data)  
        is_append_first_data = True     
    return ori_netdata, is_append_first_data

def restore_ori_netdata(ori_netdata):
    restore_info = []
    restore_index = -1
    index = len(ori_netdata) - 1
    while index > 0:
        if ori_netdata[index][10] != ori_netdata[index-1][4]:
            restore_index = index
            break
        index -= 1
    if restore_index != -1:
        restore_info = [ori_netdata[restore_index][0], ori_netdata[restore_index][1], restore_index]

    while restore_index > 0:
        try:
            ori_netdata[restore_index-1][4]  = float(ori_netdata[restore_index][4]) / (1 + float(ori_netdata[restore_index][9]))
            ori_netdata[restore_index][10]   = ori_netdata[restore_index-1][4]
            ori_netdata[restore_index-1][10] = float(ori_netdata[restore_index-1][4]) / (1 + float(ori_netdata[restore_index-1][9]))
            ori_netdata[restore_index-1][3]  = float(ori_netdata[restore_index-1][4]) * float(ori_netdata[restore_index-1][12])
            ori_netdata[restore_index-1][5]  = float(ori_netdata[restore_index-1][4]) * float(ori_netdata[restore_index-1][13])
            ori_netdata[restore_index-1][6]  = float(ori_netdata[restore_index-1][4]) * float(ori_netdata[restore_index-1][14])
            restore_index -= 1
        except IndexError as e:
            print (ori_netdata[restore_index-1])
            restore_index -= 1

    return restore_info, restore_index, ori_netdata

def restore_databased_data(trans_database_data, ori_netdata):
    index = len(trans_database_data) - 1
    while index > 0:
        curr_yclose = trans_database_data[index][10]
        curr_close = trans_database_data[index][4]
        curr_pctchg = trans_database_data[index][9]
        yes_close = trans_database_data[index-1][4]
        if curr_yclose != yes_close:
            trans_database_data[index-1][4]  = float(curr_close) / (1 + float(curr_pctchg))
            trans_database_data[index][10]   = trans_database_data[index-1][4]     
            trans_database_data[index-1][10] = float(trans_database_data[index-1][4]) / (1 + float(trans_database_data[index-1][9]))
            trans_database_data[index-1][3]  = float(trans_database_data[index-1][4]) * float(trans_database_data[index-1][12])
            trans_database_data[index-1][5]  = float(trans_database_data[index-1][4]) * float(trans_database_data[index-1][13])
            trans_database_data[index-1][6]  = float(trans_database_data[index-1][4]) * float(trans_database_data[index-1][14])
        index -= 1        
    
    index = len(trans_database_data) - 2
    while index >= 0:
        ori_netdata.insert(0, trans_database_data[index])
        index -= 1
    return ori_netdata
    
def get_restore_data(databaseobj, secode, ori_netdata, isLeftInterval, first_data=[]):
    '''
    获取前复权后的数据
    @databaseobj: 指向当前写入数据的句柄
    @secode: 当前的证券代码
    @ori_netdata: 当前已经获取的网络数据
    1. 判断前复权的时间点
        -- 获取数据时，考虑了已经存在的数据，将其边界值重新获取在新的网络原始数据中。
           所以不需要从数据库中提取相关边界值用于判断复权时间
    2. 获取到复权时间后，获取并删除数据库里复权时间之前的数据。
    3. 将新的网络原始数据与数据库中获取的数据结合，并进行前复权的计算，得到最终的复权数据。
    '''
    transed_netdata, is_append_first_data = append_database_data(ori_netdata, isLeftInterval, first_data)
    restore_info, restore_index, complete_data = restore_ori_netdata(transed_netdata)
    if is_append_first_data == True:
        complete_data.pop()

    if restore_index > -1:
        # print("transed restore_index: ", restore_index, complete_data[restore_index])
        # print_list ('transed_complete_data: ', complete_data)
        pass

    if restore_index > -1 and isLeftInterval == False:
        end_restore_datatime = [complete_data[restore_index][0], complete_data[restore_index][1]]
        database_data = databaseobj.get_data_by_enddatetime(secode, end_restore_datatime)
        if len(database_data) > 0:
            # print_list('database data: ', database_data)
            restore_info[2] += len(database_data)
            databaseobj.delete_all_data(secode)
            database_data.append(complete_data[restore_index])
            complete_data = restore_databased_data(database_data, complete_data)
            # print_list ('database_transed complete_data: ', complete_data) 
    
    return complete_data, restore_info


    
