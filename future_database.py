from CONFIG import *
from database import Database

class FutureDatabase(Database):
    def __init__(self, id=0, host=DATABASE_HOST, user=DATABASE_USER, \
                pwd=DATABASE_PWD, db='Future_Info'):
        Database.__init__(self, id, host, user, pwd, db)

    def get_create_str(self, table_name):
        complete_tablename = '[%s].[dbo].[%s]' % (self.db, table_name)
        value_str = u'(Code varchar(25) not null Primary Key(Code))'
        create_str = u'create table %s %s' % (complete_tablename, value_str)
        return create_str

    def get_multi_insert_str(self, contract_list, table_name):
        col_str = u'(Code)'        
        complete_tablename = u'[%s].[dbo].[%s]' % (self.db, table_name)
        val_str = ""
        for constract in contract_list:
            val_str += u"(\'%s\')," % (constract)
        val_str = val_str[0:len(val_str)-1]
        insert_str = u"insert into %s %s values %s" \
                    % (complete_tablename, col_str, val_str)
        return insert_str

            
