# -*- coding: UTF-8 -*-

from selenium import webdriver

import time
import threading
import traceback
import sys


from announcement_newdatabase import AnnouncementNewDatabase
from CONFIG import *
from func_tool import *
from func_qt import update_tableinfo
from func_time import *
from func_secode import *

# import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector

import datetime

def output_msg(msg, table_view):
    print(msg)
    if table_view != None:
        update_tableinfo(table_view, msg)

class DownloadAnnouncement(object):
    """
    提供更新公告数据的功能
    """
    def __init__(self, dbhost, start_date, update_time = 3*60*60, \
                clear_database=False,table_view=None, error_tableview = None):
        """
        构造函数
        @table_view 指向对应显示表格的句柄
        @type QTableView
        """
        self.start_date = start_date
        self.end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.clear_database = clear_database
        self.table_view = table_view
        self.error_tableview = error_tableview
        self.dbhost = dbhost
        self.dbname = 'Announcement'
        self.updatetime = update_time
        self.dirname = STRATEGY_FILE_DIR        
        self.flag = 0
        self.driver = webdriver.PhantomJS()
        # self.driver = webdriver.Chrome()

        # print ("self.clear_database: ", self.clear_database)
        # self.dirname = "//192.168.211.182/it程序设计/strategy"
        self.init_database()
        if self.table_view != None:
            update_tableinfo(self.table_view, '新建公告下载对象')

    def init_database(self):
        self.announcement_database_obj = AnnouncementNewDatabase(db=self.dbname, host=self.dbhost)
        
    def get_sh_announcement_detail(self, sh_secode_list):
        driver = self.driver
        url = "http://www.sse.com.cn/disclosure/listedinfo/announcement/"
        driver.set_page_load_timeout(30)

        sh_announcement = {}
        for secode in sh_secode_list:
            sh_announcement[secode] = []

        secode_index = 0
        while secode_index < len(sh_secode_list):
            secode = sh_secode_list[secode_index]
            try:
                driver.get(url)
                time.sleep(3)

                inputCode = driver.find_element_by_id('inputCode')    
                inputCode.send_keys(secode)
                time.sleep(1)

                js = "$('input[id=start_date]').attr('readonly',false)"  # 3.jQuery，设置为false
                driver.execute_script(js)
                inputStartTime = driver.find_element_by_id('start_date')
                inputStartTime.send_keys(self.start_date)
                # print (inputStartTime.get_attribute('value'))
                time.sleep(1)

                js = "$('input[id=end_date]').attr('readonly',false)"  # 3.jQuery，设置为false
                driver.execute_script(js)
                inputEndTime = driver.find_element_by_id('end_date')
                inputEndTime.send_keys(self.end_date)
                # print (inputEndTime.get_attribute('value'))

                time.sleep(1)

                driver.find_element_by_id('btnQuery').click()
                time.sleep(2)

                html = driver.page_source.encode('utf-8')
                html_response = HtmlResponse(driver.current_url, body=html, encoding='utf-8')
                sel = Selector(html_response)
                # html_response = scrapy.http.HtmlResponse(driver.current_url, body=html, encoding='utf-8')
                # sel = scrapy.Selector(html_response)

                announcement_info = []
                announcement_info = sel.xpath('//em[@class="pdf-first"]/a/text()').extract()
                href_info = sel.xpath('//em[@class="pdf-first"]/a/@href').extract()  
                time_info = sel.xpath('//dd[@class="just_this_only"]/span/text()').extract()

                if len(announcement_info) > 300:
                    continue

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
                    if tmp_list[0] in sh_secode_list:
                        sh_announcement[tmp_list[0]].append([cur_an, href, an_time])

                if self.start_date !=  self.end_date:
                    today_time_info = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    msg = "%s: %s 至 %s 前的公告数: %d" % (secode, self.start_date, today_time_info, len(announcement_info))
                else:
                    today_time_info = datetime.datetime.now().strftime("%H:%M:%S")
                    msg = "%s 今天%s前的公告数: %d" % (secode, today_time_info, len(announcement_info))
                    
                output_msg(msg, self.table_view)
                secode_index += 1
            except Exception as e:
                exception_info = "\n" + str(traceback.format_exc()) + '\n'
                driver_error = "driver.get(url)"
                if driver_error in exception_info:
                    errorMsg = "获取 %s 公告失败, 重新进行获取" % (secode)
                    print (errorMsg)
                    if self.error_tableview != None:
                        update_tableinfo(self.error_tableview, errorMsg)
                else:
                    raise(e)

        return sh_announcement

    def get_sz_announcement_detail(self, sz_secode_list):
        driver = self.driver
        url = "http://www.szse.cn/disclosure/listed/notice/index.html"
        sz_announcement = {}
        driver.set_page_load_timeout(30)

        http_prex = "http://www.szse.cn"

        secode_index = 0
        while secode_index < len(sz_secode_list):
            secode = sz_secode_list[secode_index]
            try:
                driver.get(url)
                time.sleep(3)

                driver.find_element_by_id('input_code').send_keys(secode)
                time.sleep(1)
                
                inputStartTime = driver.find_element_by_id('startTime')
                inputStartTime.clear()
                inputStartTime.send_keys(self.start_date)
                time.sleep(1)

                inputEndTime = driver.find_element_by_id('endTime')
                inputEndTime.clear()
                inputEndTime.send_keys(self.end_date)                
                time.sleep(1)

                driver.find_element_by_name('imageField').click()
                time.sleep(3)

                html = driver.page_source.encode('utf-8')
                html_response = HtmlResponse(driver.current_url, body=html, encoding='utf-8')
                sel = Selector(html_response)

                # html_response = scrapy.http.HtmlResponse(driver.current_url, body=html, encoding='utf-8')
                # sel = scrapy.Selector(html_response)

                announcement_info = []        
                announcement_info = sel.xpath('//td[@class="td2"]/a/text()').extract()    
                href_info = sel.xpath('//td[@class="td2"]/a/@href').extract()  
                time_info = sel.xpath('//td[@class="td2"]/span/text()').extract()    
                # print_data(secode + " announcement_info: ", announcement_info)  
                # print_data(secode + " href_info: ", href_info)  
            
                for i in range(len(href_info)):
                    href_info[i] = http_prex + href_info[i]
                
                sz_announcement[secode] = []
                for i in range(len(announcement_info)):      
                    an_time = time_info[i]
                    an_time = an_time.replace('[', '')
                    an_time = an_time.replace(']', '')       
                    an_time = an_time.replace('-', '')
                    # print an_time, secode, announcement_info[i]
                    sz_announcement[secode].append([announcement_info[i], href_info[i], an_time])
                
                if self.start_date !=  self.end_date:
                    today_time_info = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    msg = "%s: %s 至 %s 前的公告数: %d" % (secode, self.start_date, today_time_info, len(announcement_info))
                else:
                    today_time_info = datetime.datetime.now().strftime("%H:%M:%S")
                    msg = "%s 今天%s前的公告数: %d" % (secode, today_time_info, len(announcement_info))

                output_msg(msg, self.table_view)      
                secode_index += 1
            except Exception as e:
                exception_info = "\n" + str(traceback.format_exc()) + '\n'
                driver_error = "driver.get(url)"
                if driver_error in exception_info:
                    errorMsg = "获取 %s 公告失败, 重新进行获取" % (secode)
                    output_msg(msg, self.error_tableview)
                else:
                    raise(e)
            
        return sz_announcement

    def get_secode_list(self):    
        secode_list = get_excel_secode(self.dirname)

        # secode_list = ["601198", "000695"]

        sz_secode_list = []
        sh_secode_list = []
        for secode in secode_list:
            if secode.startswith('0') or secode.startswith('3'):
                sz_secode_list.append(secode)
            if secode.startswith('6'):
                sh_secode_list.append(secode)
        sz_secode_list = []
        # sh_secode_list = sh_secode_list[0:1]
        # sz_secode_list = sz_secode_list[0:1]
        # sh_secode_list = ['600068']
        # print (sz_secode_list)

        return sz_secode_list, sh_secode_list

    def get_announcement(self, sz_secode_list, sh_secode_list):
        sh_announcement = self.get_sh_announcement_detail(sh_secode_list)  
        sz_announcement = self.get_sz_announcement_detail(sz_secode_list)      
         
        return sz_announcement, sh_announcement

    def store_annnouncement(self):        
        self.flag += 1
        if self.flag > 1:
            self.start_date = self.end_date
            self.clear_database = 'False'

        if self.clear_database == 'True':
            msg = "清空当前公告数据库"
            output_msg(msg, self.table_view)
            self.announcement_database_obj.clearDatabase()

        msg = "开始获取公告数据"
        output_msg(msg, self.table_view)

        sz_secode_list, sh_secode_list = self.get_secode_list()
        secode_list = sz_secode_list + sh_secode_list
        self.announcement_database_obj.completeDatabaseTable(secode_list)

        sz_announcement, sh_announcement = self.get_announcement(sz_secode_list, sh_secode_list)
        for secode in secode_list:
            if secode in sh_secode_list and len(sh_announcement[secode]) != 0:           
                for item in sh_announcement[secode]:
                    self.announcement_database_obj.insert_data(secode, item[2], item)
            elif secode in sz_secode_list and len(sz_announcement[secode]) != 0:
                for item in sz_announcement[secode]:
                    self.announcement_database_obj.insert_data(secode, item[2], item)        
        
        if self.start_date !=  self.end_date:
            today_time_info = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = '%d 家公司, %s 至 %s 前所有公告获取完成' %(len(secode_list), self.start_date, today_time_info)
        else:
            today_time_info = datetime.datetime.now().strftime("%H:%M:%S")
            msg = '%d 家公司今天%s 前的所有公告获取完成' %(len(secode_list),today_time_info)

        output_msg(msg, self.table_view)

        if isAnnouncementOver():
            waitForNextDay(table_view=self.table_view)
            self.store_annnouncement()
        else:
            msg = '%d 小时后, 再获取各公司最新公告' % (self.updatetime / 60 / 60)
            output_msg(msg, self.table_view)

            timer = threading.Timer(self.updatetime, self.store_annnouncement, args=())
            timer.start()

    def main(self):
        try:
            self.store_annnouncement()
        except Exception as e:
            exception_info = str(traceback.format_exc())
            print (exception_info)
            exception_info = exception_info.split('\n')            
            if self.error_tableview != None:
                for info in exception_info:
                    update_tableinfo(self.error_tableview, info)
            
def download_announcement_main(dbhost, start_date, update_time= 20, clear_database = False, \
                                table_view=None, error_tableview = None):   
    msg = "链接的数据库为: %s" %(dbhost)
    output_msg(msg, table_view)
    print(dbhost, update_time, start_date, clear_database)
    
    download_announcement_obj = DownloadAnnouncement(dbhost= dbhost, \
                                                    start_date= start_date, \
                                                    update_time= update_time, \
                                                    clear_database= clear_database, \
                                                    table_view=table_view, \
                                                    error_tableview=error_tableview) 
    download_announcement_obj.main()

if __name__ == "__main__":
    dbhost = '192.168.211.165'
    start_date = datetime.datetime.now() + datetime.timedelta(days=-10)
    start_date = start_date.strftime('%Y-%m-%d')
    update_time = 20
    clear_database = False
    download_announcement_main(dbhost, start_date=start_date, update_time=update_time, \
                                clear_database=clear_database)
    # get_sh_announcement()
    # get_sz_announcement()
    # get_secode_name()
    # get_announcement()
    # test_get_sz_announcement_detail()
    # test_get_announcement_detail()