import logging
import traceback
import time

def LoggerLevelFunc(msg:str=None):
    def AddExceptionFuncInner(func):
        def wrapper(*args, **kwargs):
            try:
                start_time = time.time()
                func()  
                end_time = time.time()
                print("msg:%s, Cost Time: %s", msg, str(end_time - start_time))
                
            except Exception as e:
                print("[Decorator]: " + traceback.format_exc())    
        return wrapper
    return AddExceptionFuncInner
    
            
            
def LogFunc(func):
    def wrapper():
        start_time = time.time()
        func()  
        end_time = time.time()
        print("Cost Time: " + str(end_time - start_time))
    
    return wrapper

    # start_time = 

@LoggerLevelFunc(msg="One")
def test1():
    time.sleep(1)
    raise RuntimeError("User exception")
    # a = 1/0
    
def run_time(func):
    def wrapper():
        start = time.time()
        func()                  # 函数在这里运行
        end = time.time()
        cost_time = end - start
        print("func three run time {}".format(cost_time))
    return wrapper

@run_time
def fun_one():
    time.sleep(3)
   
    
@run_time
def fun_two():
    time.sleep(3)
    
@run_time
def fun_three():
    time.sleep(3)

def logger(msg=None):
    def run_time_inner(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            func()                  # 函数在这里运行
            end = time.time()
            cost_time = end - start
            print("[{}] func three run time {}".format(msg, cost_time))
        return wrapper
    return run_time_inner

@logger(msg="Two")
def TestOne():
    time.sleep(1)

if __name__ == '__main__':
    # test1()
    TestOne()
    