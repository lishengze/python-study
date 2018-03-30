# -*- coding: UTF-8 -*-
# encoding=utf8 
from selenium import webdriver
from scrapy.http import HtmlResponse
import time
import scrapy
import threading

import sys

from toolFunc import *
from announcement_database import AnnouncementDatabase
from announcement_newdatabase import AnnouncementNewDatabase
from CONFIG import *

reload(sys) 
sys.setdefaultencoding('utf8')

def removeErrorChar(oriStr):
    errorChar = ['(', ')', '（', '）']
    for char in errorChar:
        if char in oriStr:
            oriStr = oriStr.replace(char, '')
    return oriStr

def print_data(msg, data):
    print "\n", msg, len(data)
    datanumb = 100
    # if len(data) > datanumb:
    #     data = data[0:datanumb]

    for item in data:
        print item

def get_sh_announcement_detail(sh_secode_list):
    driver = webdriver.PhantomJS()
    url = "http://www.sse.com.cn/disclosure/listedinfo/announcement/"

    driver.set_page_load_timeout(30)
    driver.get(url)
    time.sleep(5)

    sh_announcement = {}
    for secode in sh_secode_list:
        sh_announcement[secode] = []

    for secode in sh_secode_list:
        driver.get(url)
        time.sleep(2)

        inputCode = driver.find_element_by_id('inputCode')
        inputCode.clear()        
        inputCode.send_keys(secode)

        driver.find_element_by_id('btnQuery').click()
        time.sleep(2)

        html = driver.page_source.encode('utf-8')
        html_response = HtmlResponse(driver.current_url, body=html, encoding='utf-8')

        sel = scrapy.Selector(html_response)

        announcement_info = sel.xpath('//em[@class="pdf-first"]/a/text()').extract()
        href_info = sel.xpath('//em[@class="pdf-first"]/a/@href').extract()  
        time_info = sel.xpath('//dd[@class="just_this_only"]/span/text()').extract()
        # print time_info

        # print 'announcement_info: ', announcement_info
        # print 'href_info: ', href_info

        for i in range(len(announcement_info)):
            announcement = announcement_info[i]
            href = href_info[i]
            if ':' in announcement:
                tmp_list = announcement.split(':')
            elif '：' in announcement:
                tmp_list = announcement.split('：')
            else:
                continue

            an_time = time_info[i].replace('-','')
            cur_an = tmp_list[1]
            print an_time, tmp_list[0], cur_an 
            if tmp_list[0] in sh_secode_list:
                sh_announcement[tmp_list[0]].append([cur_an, href, an_time])

    return sh_announcement

def get_sz_announcement_detail(sz_secode_list):
    driver = webdriver.PhantomJS()
    # driver = webdriver.Chrome()
    url = "http://disclosure.szse.cn/m/drgg.htm"
    sz_announcement = {}
    driver.set_page_load_timeout(30)

    http_prex = "http://disclosure.szse.cn/m/"

    for secode in sz_secode_list:
        driver.get(url)
        time.sleep(2)

        end_date = datetime.datetime.now()
        start_date = end_date + datetime.timedelta(days=-10)
        
        inputStartTime = driver.find_element_by_id('startTime')
        inputStartTime.clear()
        inputStartTime.send_keys(start_date.strftime('%Y-%m-%d'))

        inputEndTime = driver.find_element_by_id('endTime')
        inputEndTime.clear()
        inputEndTime.send_keys(end_date.strftime('%Y-%m-%d'))

        driver.find_element_by_id('stockCode').send_keys(secode)
        driver.find_element_by_name('imageField').click()
        time.sleep(2)

        html = driver.page_source.encode('utf-8')
        html_response = HtmlResponse(driver.current_url, body=html, encoding='utf-8')
        sel = scrapy.Selector(html_response)
        announcement_info = sel.xpath('//td[@class="td2"]/a/text()').extract()    
        href_info = sel.xpath('//td[@class="td2"]/a/@href').extract()  
        time_info = sel.xpath('//td[@class="td2"]/span/text()').extract()    
        # print_data(secode + " announcement_info: ", announcement_info)  
        # print_data(secode + " href_info: ", href_info)  
       
        for i in range(len(href_info)):
            href_info[i] = http_prex + href_info[i]
        
        sz_announcement[secode] = []
        if len(announcement_info) != 0:
            for i in range(len(announcement_info)):      
                an_time = time_info[i]
                an_time = an_time.replace('[', '')
                an_time = an_time.replace(']', '')       
                an_time = an_time.replace('-', '')
                print an_time, secode, announcement_info[i]
                sz_announcement[secode].append([announcement_info[i], href_info[i], an_time])
        
    return sz_announcement

def get_secode_list(dirname):    
    secode_list = get_excel_secode(dirname)
    # print_data("secode_list: ", secode_list)

    sz_secode_list = []
    sh_secode_list = []
    for secode in secode_list:
        if secode.startswith('0') or secode.startswith('3'):
            sz_secode_list.append(secode)
        if secode.startswith('6'):
            sh_secode_list.append(secode)
    return sz_secode_list, sh_secode_list

def get_announcement(sz_secode_list, sh_secode_list):
    sh_announcement = get_sh_announcement_detail(sh_secode_list)
    sz_announcement = get_sz_announcement_detail(sz_secode_list)    
    return sz_announcement, sh_announcement

def store_annnouncement(announcement_database_obj):
    if isAnnouncementOver():
        waitForNextDay()

    # dirname = u"//192.168.211.182/it程序设计/strategy"
    dirname = STRATEGY_FILE_DIR
    sz_secode_list, sh_secode_list = get_secode_list(dirname)
    # sz_secode_list = ['000001']
    # sh_secode_list = ['600682']
    secode_list = sz_secode_list + sh_secode_list
    announcement_database_obj.completeDatabaseTable(secode_list)
    sz_announcement, sh_announcement = get_announcement(sz_secode_list, sh_secode_list)

    # print_dict_data("sh_announcement: ", sh_announcement)
    # print_dict_data("sz_announcement: ", sz_announcement)

    count = 0
    for secode in secode_list:
        if secode in sh_secode_list and len(sh_announcement[secode]) != 0:
            count += 1             
            for item in sh_announcement[secode]:
                # print secode, item
                announcement_database_obj.insert_data(secode, item[2], item)
        elif secode in sz_secode_list and len(sz_announcement[secode]) != 0:
            count += 1
            for item in sz_announcement[secode]:
                # print secode, item
                announcement_database_obj.insert_data(secode, item[2], item)
    
    print "Announcement numb: ", count

    global updatetime
    timer = threading.Timer(updatetime, store_annnouncement, args=(announcement_database_obj,))
    timer.start()

def main():
    global updatetime
    updatetime = 2 * 60 * 60

    host = "192.168.211.165"
    dbname = "Announcement"
    announcement_database_obj = AnnouncementNewDatabase(db=dbname, host=host)    
    # announcement_database_obj.clearDatabase()
    store_annnouncement(announcement_database_obj)

def test_get_announcement_detail():
    sz_secode_list = ["000671"]
    get_sz_announcement_detail(sz_secode_list)
    sh_secode_list = ['600000']
    get_sh_announcement_detail(sh_secode_list)

if __name__ == "__main__":
    main()
    # get_sh_announcement()
    # get_sz_announcement()
    # get_secode_name()
    # get_announcement()
    # test_get_sz_announcement_detail()
    # test_get_announcement_detail()