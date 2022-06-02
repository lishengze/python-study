class Foo(object):
    def __init__(self):
        self.__test_name = "hhh"
    def func(self):
        print("Foo.func")
        pass

class Foo2(Foo):
    def __init__(self):
        super().__init__()
        print(self.__test_name)


def test1():
    #实例化
    obj = Foo()

    # 执行方式一:调用的func是方法
    obj.func() #func 方法

    # 执行方式二：调用的func是函数
    Foo.func(123) # 函数    
    
def test2():
    obj2 = Foo2()
    print(dir(obj2))

if __name__ == '__main__':
    test2()
