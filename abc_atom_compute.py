import os

class ABCAtomCompute(object):
    '''
    用于ABC 策略计算的原子模型
    @secode: 证券代码名称
    @fall_value: 单日下降幅度, 
    @rebound_rise_value: 反弹上升幅度-与Pmin比较;
    @rebound_fall_value: 反弹下降幅度-与Pmax比较;
    @rise_fall_price_type: 计算涨跌幅的价格选择;
    @buy_sale_price_type: 计算进出场的价格选择;
    逻辑:
        针对每一只股票的历史行情计算
    '''
    def __init__(self, secode, hist_data, fall_value, rebound_rise_value, rebound_fall_value, \
                rise_fall_price_type='close', buy_sale_price_type='close'):
        self.secode = secode
        self.fall_value = fall_value
        self.rebound_rise_value = rebound_rise_value
        self.rebound_fall_value = rebound_fall_value
        self.rise_fall_price_type = rise_fall_price_type
        self.buy_sale_price_type = buy_sale_price_type

    def compute_atom(self):
        pass



def test():
    pass

if __name__ == "__main__":
    test()