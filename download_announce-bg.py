# -*- coding: UTF-8 -*-
# encoding=utf8 
from selenium import webdriver
from scrapy.http import HtmlResponse
import time
import scrapy
import threading

import sys

from wind import Wind
from toolFunc import *
from announcement_database import AnnouncementDatabase
from announcement_newdatabase import AnnouncementNewDatabase

reload(sys) 
sys.setdefaultencoding('utf8')

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

    html = driver.page_source.encode('utf-8')
    html_response = HtmlResponse(driver.current_url, body=html, encoding='utf-8')

    sel = scrapy.Selector(html_response)

    # title_text = sel.xpath('//head/title/text()').extract()
    # print_data("title_text: ", title_text)

    announcement_info = sel.xpath('//em[@class="pdf-first"]/a/text()').extract()
    href_info = sel.xpath('//em[@class="pdf-first"]/a/@href').extract()  
    # print_data("href_info: ", href_info)
    # print_data("announcement_info: ", announcement_info)

    for i in range(len(announcement_info)):
        announcement = announcement_info[i]
        href = href_info[i]
        tmp_list = announcement.split('：')
        tmp_secode = tmp_list[0]
        if tmp_secode in sh_secode_list:
            # sh_announcement[tmp_secode].append([tmp_list[1], href])
            sh_announcement[tmp_secode].append(tmp_list[1])
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
        time.sleep(3)

        driver.find_element_by_id('stockCode').send_keys(secode)
        driver.find_element_by_name('imageField').click()
        time.sleep(1)

        html = driver.page_source.encode('utf-8')
        html_response = HtmlResponse(driver.current_url, body=html, encoding='utf-8')
        sel = scrapy.Selector(html_response)
        announcement_info = sel.xpath('//td[@class="td2"]/a/text()').extract()    
        href_info = sel.xpath('//td[@class="td2"]/a/@href').extract()  
        # print_data(secode + " announcement_info: ", announcement_info)  
        # print_data(secode + " href_info: ", href_info)  

        for i in range(len(href_info)):
            href_info[i] = http_prex + href_info[i]
        
        # sz_announcement[secode] = [announcement_info, href_info]
        sz_announcement[secode] = announcement_info
        

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
        return

    dirname = u"//192.168.211.182/1分钟数据 20160910-20170910/strategy"
    sz_secode_list, sh_secode_list = get_secode_list(dirname)
    secode_list = sz_secode_list + sh_secode_list
    announcement_database_obj.completeDatabaseTable(secode_list)
    sz_announcement, sh_announcement = get_announcement(sz_secode_list, sh_secode_list)

    print_dict_data("sh_announcement: ", sh_announcement)
    print_dict_data("sz_announcement: ", sz_announcement)

    count = 0
    date = datetime.datetime.now().strftime("%Y%m%d")
    for secode in secode_list:
        if secode in sh_secode_list and len(sh_announcement[secode]) != 0:
            count += 1
            for item in sh_announcement[secode]:
                announcement_database_obj.insert_data(secode, date, item)
        elif secode in sz_secode_list and len(sz_announcement[secode]) != 0:
            count += 1
            for item in sz_announcement[secode]:
                announcement_database_obj.insert_data(secode, date, item)
    
    print "count: ", count

    global updatetime
    timer = threading.Timer(updatetime, store_annnouncement, args=(announcement_database_obj,))
    timer.start()

def main():
    global updatetime
    updatetime = 2 * 60 * 60

    host = "192.168.211.165"
    dbname = "Announcement"
    announcement_database_obj = AnnouncementDatabase(db=dbname, host=host)    
    store_annnouncement(announcement_database_obj)

def main_new():
    global updatetime
    updatetime = 2 * 60 * 60

    host = "192.168.211.165"
    dbname = "AnnouncementNew"
    announcement_database_obj = AnnouncementNewDatabase(db=dbname, host=host)    
    store_annnouncement(announcement_database_obj)


def test_get_sz_announcement_detail():
    sz_secode_list = ["300187", "000564"]
    sz_announcement = get_sz_announcement_detail(sz_secode_list)
    # print_dict_data("sz_announcement: ", sz_announcement)

if __name__ == "__main__":
    main()
    main_new()
    # get_sh_announcement()
    # get_sz_announcement()
    # get_secode_name()
    # get_announcement()
    # test_get_sz_announcement_detail()

# def get_sz_announcement():
#     driver = webdriver.PhantomJS()
#     # driver = webdriver.Chrome()
#     url = "http://disclosure.szse.cn/m/drgg.htm"

#     driver.set_page_load_timeout(30)
#     driver.get(url)
#     time.sleep(3)

#     driver.find_element_by_id('stockCode').send_keys('002678')
#     driver.find_element_by_name('imageField').click()
#     # time.sleep(2)

#     # starttime = driver.find_element_by_id('startTime')
#     # starttime.send_keys('2017-01-01')
#     # endtime = driver.find_element_by_id('endTime')
#     # endtime.send_keys('2018-01-01')

#     html = driver.page_source.encode('utf-8')
#     html_response = HtmlResponse(driver.current_url, body=html, encoding='utf-8')
#     sel = scrapy.Selector(html_response)

#     announcement_info = sel.xpath('//td[@class="td2"]/a/text()').extract()
#     print_data("announcement_info: ", announcement_info)

#     # if sel.xpath('//iframe[@id="i_nr"]'):
#     #     driver.switch_to_frame("i_nr")
#     #     html = driver.page_source.encode('utf-8')
#     #     html_response = HtmlResponse(driver.current_url, body=html, encoding='utf-8')

#     #     sel = scrapy.Selector(html_response)

#     #     # title = sel.xpath('//title/text()').extract()
#     #     # print_data("title: ", title)

#     #     # announcement_info = sel.xpath('//table[@class="ggnr"]//a/text()').extract()
#     #     announcement_info = sel.xpath('//td[@class="td2"]/a/text()').extract()
#     #     # announcement_info = sel.xpath('//td[@class="td2"]')
#     #     # announcement_info = sel.xpath('//div[@id="sortAndPageAfficheDiv"]')
#     #     # announcement_info = sel.xpath('//table[@class="ggnr"]')

#     #     print_data("announcement_info: ", announcement_info)

#     # return announcement_info