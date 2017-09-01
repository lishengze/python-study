import threading, time, random
count = 0
class Counter(threading.Thread):
    def __init__(self, lock, threadName):
        super(Counter, self).__init__(name = threadName)  
        self.lock = lock
    
    def run(self):
        global count
        self.lock.acquire()
        for i in xrange(10000):
            count = count + 1
        self.lock.release()

def testInherit():	
	lock = threading.Lock()
	for i in range(5): 
		Counter(lock, "thread-" + str(i)).start()
	time.sleep(1)
	print count


# import threading, time, random
# count = 0
# lock = threading.Lock()
# def doAdd():
#     global count, lock
#     lock.acquire()
#     for i in xrange(10000):
#         count = count + 1
#     lock.release()
# for i in range(5):
#     threading.Thread(target = doAdd, args = (), name = 'thread-' + str(i)).start()
# time.sleep(2)
# print count

def main():
	testInherit();

main()