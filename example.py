#coding=utf-8

import pymssql  
  
class MSSQL:  
    def __init__(self, host="localhost", user="sa", pwd="sa", db="HistData"):  
        self.__name__ = "MSSQL"
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        # print (self.host, self.user, self.pwd, self.db)

             
    def __GetConnect(self):  
        """ 
        得到连接信息 
        返回: conn.cursor() s
        """  
        #if not self.db:  
        #    raise(NameError,"没有设置数据库信息")  
       
        self.conn = pymssql.connect(host=self.host,user=self.user,password=self.pwd,database=self.db,timeout=5,login_timeout=2,charset="utf8")  
        cur = self.conn.cursor()  
        if not cur:  
            raise(NameError,"连接数据库失败")  
        else:  
            return cur  
  
    ##验证数据库连接  
    def VerifyConnection(self):  
        try:  
            if self.host=='':  
                return False  
            conn = pymssql.connect(host=self.host,user=self.user,password=self.pwd,database=self.db,timeout=1,login_timeout=1,charset="utf8")  
            print "Connect Sucess!"
            return True  
        except:  
            print "Connect Failed!"
            return False  
  
    def ExecQuery(self,sql):  
        """ 
        执行查询语句 
        返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段 
 
        调用示例： 
                ms = MSSQL(host="localhost",user="sa",pwd="123456",db="PythonWeiboStatistics") 
                resList = ms.ExecQuery("SELECT id,NickName FROM WeiBoUser") 
                for (id,NickName) in resList: 
                    print str(id),NickName 
        """  
        cur = self.__GetConnect()  
        cur.execute(sql)  
        resList = cur.fetchall()  
        #resList = cur.description  
        #查询完毕后必须关闭连接  
        self.conn.close()  
        return resList  
  
    def ExecNonQuery(self,sql):  
        """ 
        执行非查询语句 
        调用示例： 
            cur = self.__GetConnect() 
            cur.execute(sql) 
            self.conn.commit() 
            self.conn.close() 
        """  
        cur = self.__GetConnect()  
        cur.execute(sql)  
        self.conn.commit()  
        self.conn.close()  
  
    def ExecStoreProduce(self,sql):  
        """ 
        执行插入语句 

        """  
        cur = self.__GetConnect()  
        tmp = cur.execute(sql)  
        self.conn.commit()  
        self.conn.close()  
        return tmp