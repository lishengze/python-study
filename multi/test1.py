from abc import ABC, abstractmethod

class Base(ABC):
    def __init__(self):
        self.__test = "test"
        self._value = 10
        
    def test(self):
        print(dir(self.func1))
        print(dir(Base.func1))
        self.func1()
    
    @abstractmethod
    def func1(self):
        print("Base Func1")
        

class Derived(Base):
    def __init__(self):
        self.__test = "test"
        self._value = 10
        
    def func1(self):
        print("Derived Func1")
        

def test1():
    obj_d = Derived()
    obj_d.test()
    
if __name__ == '__main__':
    test1()