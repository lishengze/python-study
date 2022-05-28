# 测试闭包的意义
# 夹带外部变量-私活 的函数， 夹带不同的私活，实现不同的功能;

def tag(tag_name:str=None):
    def add_tag(content:str=None):
        return ("{0}.{1}./{0}".format(tag_name, content))
    return add_tag

def test_tag():
    content = "hello world"
    add_tag_a = tag("a")  # 保存住了 'a' 的值, content 每次变化都不会影响到 tag_name, tag_name 一直在;
    print(add_tag_a(content))
    
    print(add_tag_a("TestContent"))
    
    add_tag_b = tag("b")
    print(add_tag_b(content))
    
# 局部变量的持久化使用;    
def create(pos=[0,0]):
    def go(direction, step):
        
        print("before compute pos[0]:{0}, pos[1]: {1}, pos.address:{2} ".format(pos[0], pos[1], id(pos)))
        new_x = pos[0] + direction[0]*step[0]
        new_y = pos[1] + direction[1]*step[1]
        
        # pos 被 go 使用，并保存了;
        pos[0] = new_x
        pos[1] = new_y
        
        print("after compute pos[0]:{0}, pos[1]: {1}, pos.address:{2} \n".format(pos[0], pos[1], id(pos)))
        
        return pos
    
    print("out compute pos[0]:{0}, pos[1]: {1}, pos.address: {2}\n".format(pos[0], pos[1], id(pos)))
    
    return go

def test_create():
    player = create()
    print(player([1,1],[10,10]))
    print(player([1,1],[10,10]))
    print(player([1,-1],[10,10]))
    
def outer_func():
    x=[0]
    def inner_func():
        # nonlocal x # 强制声明x 不是当前的局部变量;
        x[0] = x[0]+1
        
        print("inner x: {0}, x.address: {1}".format(x, id(x)))
    
        return x
        
    print("outter x: {0}, x.address: {1}".format(x, id(x)))
    inner_func()
    print("outter x: {0}, x.address: {1}".format(x, id(x)))
    
    return inner_func

def test_outer_func():
    inner = outer_func()
    
    print(inner.__closure__)
    
    inner()
    inner()
    inner()
    
def LoopOut1():
    func_list = []
    for i in range(0, 4):
        def out_func():
            return i*i
        func_list.append(out_func)
    return func_list

def LoopOut2():
    def out_func1(i):
        def inner_func():
            return i*i
        return inner_func
        
    func_list = []
    for i in range(0, 4):
        func_list.append(out_func1(i))
    return func_list
            
def test_loopout():
    func_list = LoopOut2()
    print(func_list[0]())
    print(func_list[1]())
    
    
# def outer_func():
#     x=[0]
#     def inner_func():
#         # nonlocal x # 强制声明x 不是当前的局部变量;
#         x[0] = x[0]+1
        
#         print("inner x: {0}, x.address: {1}".format(x, id(x)))
    
#         return x
        
#     print("outter x: {0}, x.address: {1}".format(x, id(x)))
#     inner_func()
#     print("outter x: {0}, x.address: {1}".format(x, id(x)))
    
#     return inner_func

import logging
from functools import partial

def wrapper_property(obj, func=None):
    if func is None:
        return partial(wrapper_property, obj)
    setattr(obj, func.__name__, func)
    return func

def logger_info(level, name=None, message=None):
    def decorate(func):
        
        logmsg = message if message else func.__name__
        
        def wrapper(*args, **kwargs):
            print("level: {0}, message: {1}".format(level, logmsg))
            return func(*args, **kwargs)

        @wrapper_property(wrapper)
        def set_level(newlevel):
            
            nonlocal level
            level = newlevel
            print("set_level: %s \n" % level)

        @wrapper_property(wrapper)
        def set_message(newmsg):
            nonlocal logmsg
            logmsg = newmsg
            print("set_message: %s \n" % logmsg)

        return wrapper

    return decorate

@logger_info(logging.WARNING)
def main(x, y):
    return x + y
    
if __name__ == '__main__':
    # test_tag()
    # test_create()
    # test_outer_func()
    # test_loopout()
    
    main(2,3)