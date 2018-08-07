from tinysoft import TinySoft


class FutureNet(TinySoft):
    def __init__(self):
        TinySoft.__init__(self)

    def get_contract_list(self, index_code):
        if index_code == '000300':
            return self.get_IF_constract_list()

    def get_IF_constract_list(self):
        tsl_str = u'return Query("沪深300指数","",True,"","代码",DefaultStockID());'
        self.curs.execute(tsl_str)
        ori_result = self.curs.fetchall()    
        result = []
        index = len(ori_result)-4
        while index < len(ori_result):
            result.append(ori_result[index][0]+'.CFE')
            index += 1
        return result

class TestFuture():
    def __init__(self):
        self.future_obj = FutureNet()
        self.test_get_IF_constract_list()

    def test_get_IF_constract_list(self):
        result = self.future_obj.get_IF_constract_list()
        print (result)

if __name__ == '__main__':
    test_future = TestFuture()
