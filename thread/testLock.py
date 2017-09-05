import threading
import time
 
num = 0
lock = threading.Lock()
rlock = threading.RLock()

def lockFunc(st):
    global num
    print (threading.currentThread().getName() + ' try to acquire the lock')
    if lock.acquire():
        print (threading.currentThread().getName() + ' acquire the lock.' )
        print (threading.currentThread().getName() +" :%s" % str(num) )
        num += 1
        time.sleep(st)
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

if __name__ == "__main__":
    # testLock()
    testRLock()
    
 
