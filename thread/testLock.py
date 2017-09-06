import threading
import time
 
num = 0
lock = threading.Lock()
rlock = threading.RLock()
cond = threading.Condition()

def lockFunc(st):
    global num
    print (threading.currentThread().getName() + ' try to acquire the lock')  
    for i in range(0,2):    
        if lock.acquire():
            print (threading.currentThread().getName() + ' acquire the lock.' )
            print "\n%s i %d"%(threading.currentThread().getName(), i)            
            # print (threading.currentThread().getName() +" :%s" % str(num) )
            # num += 1
            time.sleep(st)
            print (threading.currentThread().getName() + ' release the lock.'  )        
            lock.release()
        print (threading.currentThread().getName() + ' out of lock.acquire()!' )

def lockLoopFunc():
    print (threading.currentThread().getName() + ' try to acquire the lock')
    for i in range(0,2):    
        if lock.acquire():
            print "i %d"%(i)
            print (threading.currentThread().getName() + ' acquire the lock.' )
            time.sleep(2)
            print (threading.currentThread().getName() + ' release the lock.'  )        
            lock.release()
        print (threading.currentThread().getName() + ' out of lock.acquire()!' )

def rlockFunc(st):
    global num
    print (threading.currentThread().getName() + ' try to acquire the rlock')
    if rlock.acquire():
        print (threading.currentThread().getName() + ' acquire the rlock.' )
        print (threading.currentThread().getName() +" :%s" % str(num) )
        num += 1
        time.sleep(st)
        print (threading.currentThread().getName() + ' release the rlock.'  )        
        rlock.release()
    print (threading.currentThread().getName() + ' out of rlock.acquire()!' )  

def condFunc(st):
    global num
    print (threading.currentThread().getName() + ' try to acquire the condtion')
    if cond.acquire():
        print (threading.currentThread().getName() + ' acquire the condtion.' )
        print (threading.currentThread().getName() +" :%s" % str(num) )
        num += 1
        time.sleep(st)
        print (threading.currentThread().getName() + ' release the condtion.'  )        
        cond.release()
    print (threading.currentThread().getName() + ' out of condtion.acquire()!' ) 

def condFunc1(st):
    global num
    print (threading.currentThread().getName() + ' try to acquire the Lock')
    print cond
    if cond.acquire():
        print (threading.currentThread().getName() + ' acquire the Lock.' )
        time.sleep(st)
        print (threading.currentThread().getName() + ' wait().' )
        cond.wait()
        print cond
        print (threading.currentThread().getName() + " become ALIVE!")
        
        # if cond.acquire():
        #     print "--- notify() don't acquire lock! ---"
        #     print cond

        print (threading.currentThread().getName() + ' release the Lock.'  )        
        cond.release()
    print (threading.currentThread().getName() + ' out of condtion.acquire()!' )   
    print cond      

def condFunc2(st):
    global num
    print (threading.currentThread().getName() + ' try to acquire the Lock')
    print cond
    if cond.acquire():
        print '+++ wait() will release lock! +++'
        print cond
        print (threading.currentThread().getName() + ' acquire the Lock.' )

        time.sleep(st)
        print (threading.currentThread().getName() + ' notify().'  )     
        cond.notify()   
        time.sleep(5)
        # print (threading.currentThread().getName() + ' release the Lock.'  )     
        cond.release()
    print (threading.currentThread().getName() + ' out of condtion.acquire()!' )   
    print cond     

def testLock():
    t1 = threading.Thread(target=lockFunc, args=(8,))
    t2 = threading.Thread(target=lockFunc, args=(4,))
    t3 = threading.Thread(target=lockFunc, args=(2,))
    t1.start()
    t2.start()
    t3.start()      

def testRLock():
    t1 = threading.Thread(target=rlockFunc, args=(8,))
    t2 = threading.Thread(target=rlockFunc, args=(4,))
    t3 = threading.Thread(target=rlockFunc, args=(2,))
    t1.start()
    t2.start()
    t3.start()      

def testConditionLock():
    t1 = threading.Thread(target=condFunc, args=(8,))
    t2 = threading.Thread(target=condFunc, args=(4,))
    t3 = threading.Thread(target=condFunc, args=(2,))
    t1.start()
    t2.start()
    t3.start()       

def testConditionPV():
    t1 = threading.Thread(target=condFunc1, args=(8,))
    t2 = threading.Thread(target=condFunc2, args=(4,))
    t1.start()
    t2.start()

if __name__ == "__main__":
    # lockLoopFunc()
    testLock()
    # testRLock()
    # testConditionLock()
    # testConditionPV()
    
 
