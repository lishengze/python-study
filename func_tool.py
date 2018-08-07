# -*- coding: UTF-8 -*-
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
       
def LogInfo(wfile, info):
    try:
        wfile.write(info)    
        print (info)    
    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] LogInfo Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo   
        raise(e) 
        
def pure_dict_data(ori_data):
    pop_list = []
    for item in ori_data:
        if len(ori_data[item]) == 0:
            pop_list.append(item)
    for item in pop_list:
        ori_data.pop(item)
    return ori_data

def get_filename_array(dirname):
    file_name = os.listdir(dirname)
    return file_name

def get_restore_info(secode, ori_netdata, latestdata=[], firstdata=[]):
    # ori_netdata.sort(cmp=cmp_net_time, key=itemgetter(0))     
    restore_data = []
    if len(ori_netdata) < 2:
        return restore_data

    ori_netdata.sort(key=lambda x: get_time_key(x[0]))

    # 与可能需要复权的前面数据进行比较。
    if len(firstdata)!= 0:
        i = len(ori_netdata) - 1
        # print "i: ", i, ori_netdata[i]
        ori_time = [int((ori_netdata[i][0])), int((ori_netdata[i][0]))]
        first_time = [firstdata[0], firstdata[1]]
        while not is_time_late(ori_time, first_time) and i > 0:
            i -= 1
            # print "i: ", i, ori_netdata[i]
            ori_time = [int((ori_netdata[i][0])), int((ori_netdata[i][0]))]

        yclose = float(firstdata[10])
        close = float(ori_netdata[i][3])
        if  yclose != close and i > 0:
            restore_data.append(secode)
            restore_data.append(firstdata[0])
            restore_data.append(firstdata[1])
            # print "first restore data: ", restore_data 

    i = len(ori_netdata) - 1    
    # 遍历当前下载的原始数据，考察是否需要复权；
    while i > 0 and len(restore_data) == 0:
        if ori_netdata[i][8] != ori_netdata[i-1][3]:
            restore_data.append(secode)
            restore_data.append(int((ori_netdata[i][0])))
            restore_data.append(int((ori_netdata[i][0])))
            # print "i: ", i, ",", ori_netdata[i]
            # print "ori restore data: ", restore_data
            break
        i -= 1

    
    # 与已存储的最新数据比较，是否存在复权;
    if len(restore_data) == 0 and len(latestdata) != 0 :
        i = 0
        ori_time = [int((ori_netdata[i][0])), int((ori_netdata[i][0]))]
        lastest_time = [latestdata[0], latestdata[1]]

        if float(ori_netdata[i][8]) != float(latestdata[4]) and \
            is_time_late(lastest_time, ori_time):
            restore_data.append(secode)
            restore_data.append(int((ori_netdata[i][0])))
            restore_data.append(int((ori_netdata[i][0])))
            # print "i: ", i, ",", ori_netdata[i]
            # print "latest restore data: ", restore_data

    return restore_data

def compute_restore_data(sort_data):
    sort_data = list(sort_data)
    i = len(sort_data) - 1
    while i > 0:
        sort_data[i] = list(sort_data[i])
        sort_data[i-1] = list(sort_data[i-1])
        sort_data[i-1][2] = sort_data[i][2] / (1 + sort_data[i][3])
        sort_data[i][4] = sort_data[i-1][2]
        i -= 1
        
    if i > -1:
        sort_data[i] = list(sort_data[i])
        sort_data[i][4] = sort_data[i][2] / (1 + sort_data[i][3])
    return sort_data

def get_restore_time_list(ori_restore_data):
    restore_time_array = []
    for item in ori_restore_data:
        if len(ori_restore_data) == 3:
            if [item[1], item[2]] not in restore_time_array:
                restore_time_array.append([item[1], item[2]])
    return restore_time_array

def allocate_data(oridata, count):    
    result = []
    if [] in oridata:
        oridata.remove([])
    for j in range(count):
        result.append([])

    i = 0
    while i < len(oridata):
        j = 0
        while j < count and i + j < len(oridata):
            result[j].append(oridata[i+j])
            j += 1
        i += j

    if [] in result:
        result.remove([]) 
    return result   

def pop_dict_item(dict_data, poped_list):
    for item in poped_list:
        if item in dict_data:
            dict_data.pop(item)

def deep_copy_list(ori_list):
    des_list = []
    for item in ori_list:
        des_list.append(item)
    return des_list

def create_array(start_value, step, end_value, denominator = 100):
    result = []
    if step < 0:
        while start_value >= end_value:
            result.append(start_value/100)
            start_value += step
    else:
        while start_value <= end_value:
            result.append(start_value/100)
            start_value += step
    return result

def trans_matrix(ori_data):
    result = []
    for col_index in range(len(ori_data[0])):
        result.append([])
        for row_index in range(len(ori_data)):
            result[col_index].append(ori_data[row_index][col_index])
    return result

def get_annualized_return(earning_list):
    sum_earning = earning_list[len(earning_list)-1]
    year_days = 243
    years = len(earning_list) / year_days 
    result = sum_earning ** (1/years) - 1
    # print('sum_earning: ', sum_earning, ' years: ', years)

    # date_year = []
    # for data in date_list:
    #     date_year.append(int(data / 10000))
    # index = 0
    # count = 0
    # year = []
    # while index < len(date_year) - 1:
    #     if date_year[index] == date_year[index + 1]:
    #         count += 1
    #     else:
    #         year.append(count)
    #         count = 0

    # for data in date_year:
    #     pass
        
    return result

def add_dict_item (ori_dict, added_dict):
    for item in added_dict:
        if item not in ori_dict:
            ori_dict[item] = added_dict[item]
    return ori_dict

def remove_dict_item(ori_dict, removed_list):
    for item in removed_list:
        if item in ori_dict:
            ori_dict.pop(item)
    return ori_dict

def add_list_item(ori_list, added_list):
    for item in added_list:
        if item not in ori_list:
            ori_list.append(item)
    return ori_list

def remove_list_item(ori_list, removed_list):
    for item in removed_list:
        if item in ori_list:
            ori_list.remove(item)
    return ori_list

def get_value_list(data_numb, value = 0):
    result = []
    index = 0
    while index < data_numb:
        result.append(value)
        index += 1
    return result

