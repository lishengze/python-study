# -*- coding: UTF-8 -*-
from CONFIG import *
from toolFunc import *
from database import Database

class AnnouncementDatabase(Database):
    def __init__(self, id=0, host=DATABASE_HOST, user=DATABASE_USER, pwd=DATABASE_PWD, db=DATABASE_NAME):
        Database.__init__(self, id, host, user, pwd, db)
        self.id = id

    def __del__(self):
        Database.__del__(self)

    def get_create_str(self, table_name):
        value_str = "(Secode varchar(10) not null, Date int not null, \
                     Announcement varchar(200) not null Primary Key(Date, Announcement))"
        complete_tablename = u'[' + self.db + '].[dbo].['+ table_name +']'
        create_str = "create table " + complete_tablename + value_str
        # print create_str
        return create_str

    def get_insert_str(self,secode, date, annnouncement):
        col_str = "(Secode, Date, Announcement)"
        val_str = u"\'" + str(secode) + '\', ' + str(date) + ", \'" + str(annnouncement) + "\'"
        complete_tablename = u'[' + self.db + '].[dbo].['+ secode +']'
        insert_str = "insert into "+ complete_tablename + col_str + "values ("+ val_str +")"
        print insert_str
        return insert_str

    def insert_data(self, secode, date, annnouncement):
        try:
            insert_str = self.get_insert_str(secode, date, annnouncement)
            self.changeDatabase(insert_str)
        except Exception as e:
            connect_error = "20003"
            if connect_error in e[1]:
                connFailedWaitTime = 5
                print '\n^^^^^20003 connection timed out database insert_data restart! ^^^^^ \n'
                time.sleep(connFailedWaitTime)
                self.insert_data(secode, date, annnouncement)       
            elif "Violation of PRIMARY KEY constraint" not in e[1]:
                print e
                raise(e)
