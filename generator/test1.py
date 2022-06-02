def yield_test(n): 
    for i in range(n): 
        yield call(i) 
        print("YieldTest: i=",i)     
    print("Done.") 
    
def call(i): 
    return i*2

def test1():
    for i in yield_test(5): 
        print("Test1: ", i,",")
    
if __name__ == '__main__':
    test1()