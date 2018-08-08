# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
"""
from PyQt5.QtCore import pyqtSlot, QMetaType,QDate
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication, QScrollBar
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import sys
from Ui_main import Ui_MainWindow

from func_time import getDateNow
from func_qt import update_tableinfo
from datetime import datetime
import traceback

import threading
from download_announce import download_announcement_main
from download_marketdata import download_histdata_main

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    更新历史数据的主窗口。
    """
    def __init__(self, app=None, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.app=app
        self.setupUi(self)
        self.init_commondata()
        self.initWidget()
        
    def __del__(self):
        print ('__del__')
        
    def init_commondata(self):
        self.datasource_list = ['192.168.211.162', '192.168.211.165', 'localhost']
        self.iscleardatabase_list = ['False', 'True']
        self.thread_list = []

    def initWidget(self):        
        self.init_database_comboBox()
        self.init_iscleardatabase_comboBox()
        self.init_all_table()
        self.init_datetime_edit()

    def init_database_comboBox(self):
        self.datasource_comboBox.addItems(self.datasource_list)
        self.datasource_comboBox.setCurrentIndex(0)

    def init_iscleardatabase_comboBox(self):
        self.isClearAnnDatabase_comboBox.addItems(self.iscleardatabase_list)
        self.isClearHistMarketDatabase_comboBox.addItems(self.iscleardatabase_list)
        self.isClearWeightDatabase_comboBox.addItems(self.iscleardatabase_list)

    def init_all_table(self):
        self.init_tableView(self.marketData_tableView)
        self.init_tableView(self.announcement_tableView)
        self.init_tableView(self.weightData_tableView)
        self.init_tableView(self.errorInfo_tableView)

    def init_tableView(self, table_view):
        initModel = QStandardItemModel()
        initModel.setHorizontalHeaderItem(0, QStandardItem('时间'))
        initModel.setHorizontalHeaderItem(1, QStandardItem('消息'))
        table_view.setModel(initModel)
        table_view.setColumnWidth(0, 150)
        table_view.setColumnWidth(1, 600)
        table_view.setShowGrid(False)
    
    def init_datetime_edit(self):
        self.marketdata_starttime_edit.setCalendarPopup(True)
        self.marketdata_starttime_edit.setDate(QDate.currentDate().addDays(-365))

        self.announcement_dateEdit.setCalendarPopup(True)
        self.announcement_dateEdit.setDate(QDate.currentDate().addDays(-10))

        self.weight_dateEdit.setCalendarPopup(True)
        self.weight_dateEdit.setDate(QDate.currentDate().addDays(-30))

    def update_announcement_data(self):
        dbhost = self.datasource_comboBox.currentText()
        start_date = self.announcement_dateEdit.date().toString("yyyy-MM-dd")
        update_time = 3 * 60 * 60
        clear_database = self.isClearAnnDatabase_comboBox.currentText()
        announcement_thread = threading.Thread(target=download_announcement_main, \
                                                args=(dbhost, start_date, \
                                                    update_time, clear_database,\
                                                    self.announcement_tableView, \
                                                    self.errorInfo_tableView,))
        self.thread_list.append(announcement_thread)
        announcement_thread.setDaemon(True)
        announcement_thread.start()

    def update_histMarket_data(self):
        dbhost = self.datasource_comboBox.currentText()
        clear_database = self.isClearHistMarketDatabase_comboBox.currentText()
        start_datetime = int(self.marketdata_starttime_edit.date().toString("yyyyMMdd"))
        end_datetime = getDateNow()
        source_contions = [start_datetime, end_datetime, 'stock']
        data_type_list = ['MarketData_day', 'MarketData_10m', 'MarketData_15m', \
                            'MarketData_30m', 'MarketData_60m', "'MarketData_120m"]
        # data_type_list = ['MarketData_15m']
        # data_type_list = ['MarketData_week', 'MarketData_month']
        # data_type_list = ['MarketData_week']
        # data_type_list = ['MarketData_10m']
        # data_type_list = ['MarketData_month', 'MarketData_week', \
        #                     'MarketData_day', 'MarketData_10m']        

        # data_type_list = ['MarketData_5m', 'MarketData_10m', \
        #                   'MarketData_15m', 'MarketData_30m', 'MarketData_60m']   

        msg = '开始更新历史行情, 数据库为: %s' % (dbhost)
        update_tableinfo(self.marketData_tableView, msg)

        histMarket_work_thread = threading.Thread(target=download_histdata_main, \
                                                args=(dbhost, data_type_list, 
                                                source_contions, clear_database, \
                                                self.marketData_tableView, \
                                                self.errorInfo_tableView,))
                                                
        self.thread_list.append(histMarket_work_thread)
        histMarket_work_thread.setDaemon(True)
        histMarket_work_thread.start()

    def update_weight_data(self):
        dbhost = self.datasource_comboBox.currentText()
        clear_database = self.isClearWeightDatabase_comboBox.currentText()
        start_datetime = int(self.weight_dateEdit.date().toString("yyyyMMdd"))
        end_datetime = getDateNow()
        source_contions = [start_datetime, end_datetime]
        data_type_list = ["IndustryData", "WeightData"]
        # data_type_list = ['MarketData_day']

        msg = '开始更新权重与行业分类数据, 数据库为: %s' % (dbhost)
        update_tableinfo(self.weightData_tableView, msg)

        weight_industry_work_thread = threading.Thread(target=download_histdata_main, \
                                                args=(dbhost, data_type_list, 
                                                source_contions, clear_database, \
                                                self.weightData_tableView, \
                                                self.errorInfo_tableView,))
        self.thread_list.append(weight_industry_work_thread)
        weight_industry_work_thread.setDaemon(True)
        weight_industry_work_thread.start()        

    @pyqtSlot()
    def on_startDownloadData_button_clicked(self):
        """
        Slot documentation goes here.
        """
        self.update_announcement_data()
        self.update_histMarket_data()
        self.update_weight_data()

    @pyqtSlot()
    def on_updateAnnouncement_button_clicked(self):
        """
        Slot documentation goes here.
        """
        self.update_announcement_data()

    @pyqtSlot()
    def on_updateHistMarketData_button__clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.update_histMarket_data()
        
    @pyqtSlot()
    def on_updateWeightData_button_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.update_weight_data()

    @pyqtSlot()
    def closeEvent(self, event):        
        print ('main_window_close')
        # if None != self.app:
        #     self.app.exit(0)
        #     sys.exit(0)
        # for thread in self.thread_list:
        #     thread.quit()      

if __name__ == "__main__":
    # QApplication.addLibraryPath('.')
    QApplication.addLibraryPath('./plugins')
    app = QApplication(sys.argv)
    window = MainWindow(app=app)
    window.show()
    sys.exit(app.exec_())