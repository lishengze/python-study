from WindPy import *
import datetime

def get_latest_contract_month():
    today = datetime.datetime.now()
    curr_month = today.strftime('%m')
    curr_year = today.strftime('%y')
    curr_date = today.strftime('%Y-%m-%d')
    print (curr_date)

    contract_name = 'IF%s%s.CFE' % (curr_year, curr_month)
    print (contract_name)
   
    # tmp_result = w.wsd(contract_name, "lastdelivery_date", '2018-05-02', curr_date, "")
    # print (tmp_result)

    tmp_result = w.wsd("IF1806.CFE", "lastdelivery_date", "2018-05-02", "2018-05-31", "")
    print (tmp_result)

    return curr_month


class TestMarketFunc():
    def __init__(self):
        self.__name__ = 'TestMarketFunc'
        self.test_get_latest_contract_month()

    def test_get_latest_contract_month(self):
        get_latest_contract_month()


if __name__ == '__main__':
    test_market_func = TestMarketFunc()