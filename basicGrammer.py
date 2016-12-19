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


def testFunProgram ():
    # testMapReduce()
    # testFilter()
    # testSorted()
    # testWorkSpace()
    testClosure()



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
    class Anaimal(object):
        def __init__ (self, name):
            self.__name = name
        def run (self):
            print 'Anaimal', self.__name
    
    class Mammal(Anaimal):
        def __init__ (self, name):
            self.__name = name
        def run (self):
            print 'Mammal: ' , self.__name

    class Dog(Anaimal):
        def __init__ (self, name):
            self.__name = name
        def run (self):
            print 'Dog: ' , self.__name

    class Cat(Anaimal):
        def __init__ (self, name):
            self.__name = name
        def run (self):
            print 'Cat: ' , self.__name    

    objList = [Anaimal('Color'), Mammal('Strong'), Dog('Loyal'), Cat('Proud')]
    
    for obj in objList:
        print obj
        obj.run()

def testObjectOriented():
    testPoly()

def testAll ():
    # testFunProgram()
    # testModule()
    testObjectOriented()