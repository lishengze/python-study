# -*- coding: utf-8 -*-
 
a = '默认编码是ascii'
# print a, len(a)
# for c in a:
#     print c
     
# b = unicode (a, "utf-8")
# print b,len(b)
# for c in b:
#     print c

# 递归函数
def fact(n):
    if n == 1:
        return 1
    else:
        return n * fact(n-1)

# print  fact(5)


# 生成器, 作用不明显。

# generator = (x * x for x in range(1,11))
# for value in generator:
#     print value 

def testGenerator ():
    def fib(value):
        print "step 1"
        yield 1
        print "step 2"
        yield 2
        print "step 3"
        yield 3

    for value in fib(5):
        print value

# testGenerator()

# 函数式编程
# 纯粹的函数编程没有参数， 所以没有副作用;
# python 的函数可以有参数， 所以有副作用;
# map函数： map (fn, list), fn 单独作用在list的每个元素中;
# reduce函数： reduce (fn , list), fn 作用在当前list元素后将结果与下一个元素作为参数再带入进行计算，复合式的算法。
# filter:
# sorted
def testMapReduce ():
    def userStr2Int (strValue):
        def char2num (s):
            return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}[s]
        def fn (x,y):
            return x * 10 + y
        return reduce (fn, map(char2num, strValue))

    print userStr2Int("123")

def testFilter ():
    def isOdd (value):
        return value % 2 == 1
    
    print filter(isOdd, [1,2,3,4])

def testSorted ():
    def cmpIgnoreCase (str1, str2):        
        str1 = str1.upper()
        str2 = str2.upper()
        print str1, ' ', str2
        if str1 < str2 :
            return -1
        if str2 > str2 :
            return 1
        return 0
    print sorted(["Adam", "Adele", "Bela"], cmpIgnoreCase)

def testWorkSpace ():
    for value in [5,4,3,2,1]:
        print value
    print value

def testClosure ():
    def count ():
        fs = []
        for i in range(1,4):
            def f (j):
                def g() :
                    return j * j
                return g
            fs.append(f(i))
        return fs
    fn = count()
    for val in fn :
        print val()

def testFor ():
    obj = {
        'name': 'lee',
        'age': 20
    }
    for value in obj:
        print value, obj[value]

def testForin ():
    tmp = ['a', 'b', 'c']
    if 'a' not in tmp or  'a' == 'a':
        print 'True'

def testStrFind():
    tmp = "abcde"
    print tmp.find("abd")

def testDictStr():
    a = "{'a': 'hi', 'b': 'there'}"
    print a
    print type(a)    

    b = eval(a)
    print b
    print type(b)    

    c = str(b)
    print c
    print type(c)

    d = eval(c)
    print d
    print type(d)

def testString():
    data = '[HEAD][RSP]149274176706700' + '\n' + \
        'TopAgent'+ '\n' + \
        'AllEvent'+ '\n' + \
        'AllClient'+ '\n' + \
        'FlowApp'+ '\n' + \
        'AllAgent'+ '\n' + \
        'AllTest'+ '\n' + \
        'Front50Test'+ '\n' + \
        'AllFront'+ '\n' + \
        'AllInternal'+ '\n' + \
        'AllSlog'+ '\n' + \
        'AllQuery'+ '\n' + \
        'AllProbe'+ '\n' + \
        'New'+ '\n' + \
        'AllPTestProbe'+ '\n' + \
        'AllManager'+ '\n' + \
        'MidAgent'+ '\n' + \
        'AllServices'
    data_array = data.split('\n')
    print data
    print data_array
    

def testFunProgram ():
    # testMapReduce()
    # testFilter()
    # testSorted()
    # testWorkSpace()
    # testFor()
    # testForin()
    # testStrFind()
    # testDictStr()
    testString()
    # testClosure()



# 模块机制
# 复用代码，减少命名冲突， 与nodejs相似，没有要求exports输出机制。
def testImport ():
    import sys
    def testHello():
        args = sys.argv
        if len(args) == 1:
            print "Hello, World"
        elif len(args) == 2:
            print "Hello, %s!" % args[1]
        else:
            print "Too many args"
    testHello()

def testImportFileRun():
    import testImportFile as importFile
    importFile.helloImport()

def testModule ():
    # testImport()
    testImportFileRun()

# 面向对象;
# 封装：
# 继承：
# 多态：(js无法实现)
def testPoly ():
    print 'Test Object Poly'
    class Anaimal(object):
        def __init__ (self, name):
            self.__name = name
        def run (self):
            print 'Anaimal: ', self.__name
    
    class Mammal(Anaimal):
        def __init__ (self, name):
            self.__name = name
        def run (self):
            print 'Mammal: ' , self.__name

    class Dog(Anaimal):
        def __init__ (self, name):
            self.__name = name
            self.age = 10
        def run (self):
            print 'Dog: ' , self.__name

    class Cat(Anaimal):
        def __init__ (self, name):
            self.__name = name
        def run (self):
            print 'Cat: ' , self.__name    

    dog1 = Dog('Loyal')
    print getattr(dog1, 'age')

    objList = [Anaimal('Color'), Mammal('Strong'), Dog('Loyal'), Cat('Proud')]    
    
    for obj in objList:
        obj.run()
    
    husky = Dog('Dom')
    print isinstance(husky, Dog)
    print isinstance(husky,Anaimal)
    print isinstance('a', str)
    print isinstance('a', unicode)
# 测试分别给实例和对象添加属性和方法
def testAddProMethod():
    class TmpObj(object):
        def __init__ (self, name):
            self.name = name
    
    obj1 = TmpObj('lee')
    obj2 = TmpObj('tom')
    obj1.age = 10

    # print obj1.age, obj2.age
    
    from types import MethodType
    def printName(self):
        print self.name
    TmpObj.printName = MethodType(printName, None, TmpObj)
    obj1.printName()
    obj2.printName()
# 测试@property
def testProperty():
    class Student(object):
        # def __init__(self, score):
        #     self.score = score
        
        @property
        def score (self):
            return self._score
        
        @score.setter
        def score (self, value):
            if not isinstance(value, int):
                raise ValueError('value must be int')
            if value < 0 or value > 100:
                raise ValueError('value must less than 100 and bigger than 0')
            self._score = value
    
    stu1 = Student()
    stu1.score = 100
    print stu1.score
# 测试__iter__ 属性
# __iter__ : 将实例本身设置为迭代对象;
# next: 通过next来确定每次循环的操作与返回的值;
def testIterPro():
    class fib(object):
        def __init__ (self):
            self.a, self.b = 0,1
        def __iter__(self):
            return self
        def next(self):
            self.a, self.b = self.b, self.a + self.b
            if self.a > 100:
                raise StopIteration()
            return self.a 

    for val in fib():
        print val

# 测试__getitem__
# __getitem__: 重载[index]操作符, index可以是一个数值也可以是slice函数;
def testGetItem():
    class fib(object):
        def __getitem__(self, n):
            a, b = 0, 1
            for x in range(1,n):
                a,  b = b, a + b
            return a
    print fib[5]

#面向对象测试集合
def testObjectOriented():
    print 'Test Object-Oriented'
    # testPoly()
    # testAddProMethod()
    # testProperty()
    # testIterPro()
    testGetItem()

# 进程与线程
# 测试进程
def testProcess ():
    from multiprocessing import Process
    import os
    def run_proc (name):
        print 'Run child process %s (%s)...' % (name, os.getpid())

    print 'Parent proess %s.' % os.getpid()
    childProess = Process(target=run_proc, args=('test',))
    print 'Process will start.'
    # childProess.start()
    # childProess.join()
    print 'Process ends.'

# 测试进程间通讯
def testProcessCom () :
    from multiprocessing import Process, Queue
    import os, time, random

    def write (q):
        for value in ['a', 'b', 'c']:
            print 'Put %s in queue' % value
            q.put(value)
            time.sleep(random.random())
    
    def read (q):
        while True:
            value = q.get(True)
            print 'Get %s from queue' % value
    q = Queue()
    pw = Process(target = write, args = (q,))
    pr = Process(target = read, args = (q,))
    pw.start()
    pr.start()
    pw.join()
    pr.terminate()

# 测试线程锁机制
balance = 0
def testThreadLock () :   
    import time, threading
    lock = threading.Lock()
    def change_it(n):
        global balance
        balance = balance + n
        balance = balance - n

    def run_thread(n):
        for i in range(100000):
            lock.acquire()
            try :
                change_it(n)
            finally:
                lock.release()
    
    t1 = threading.Thread(target=run_thread, args=(5,))
    t2 = threading.Thread(target=run_thread, args=(8,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print balance

# 测试线程Local变量
def testThreadLocal ():
    import threading
    local_school = threading.local()

    def process_student():
        print 'Hello, %s (in %s)' % (local_school.student, threading.current_thread().name)
    def proess_thread (name) :
        local_school.student = name
        process_student()

    t1 = threading.Thread(target=proess_thread, args=('Alice',), name='Thread-A')
    t2 = threading.Thread(target=proess_thread, args=('Bella',), name='Thread-B')
    t1.start()
    t2.start()
    t1.join()
    t2.join()


# 测试进程与线程
def testProcessThread():
    #  testProcess()
    #  testProcessCom()
    #  testThreadLock()
     testThreadLocal()

# 测试程序汇总
def testAll ():
    testFunProgram()
    # testModule()
    # testObjectOriented()
    # testProcessThread()

if __name__ == '__main__':
    testAll()