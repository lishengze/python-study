#coding=utf-8
import threading
from time import ctime,sleep
from multiprocessing import cpu_count

print 'cpu_count %d' %(cpu_count())


def music(fileName):
    for i in range(2):
        print "I was listening to %s. %s" %(fileName,ctime())
        sleep(1)

def move(fileName):
    for i in range(2):
        print "I was at the %s! %s" %(fileName,ctime())
        sleep(5)

threads = []
t1 = threading.Thread(target=music,args=(u'爱情买卖',))
threads.append(t1)
t2 = threading.Thread(target=move,args=(u'阿凡达',))
threads.append(t2)

if __name__ == '__main__':
    for t in threads:
        t.setDaemon(True)
        t.start()
    t.join()
    print "all over %s" %ctime()