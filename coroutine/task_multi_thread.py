import asyncio
import time
import threading

def get_thread_id():
    thread_id = threading.currentThread().ident
    return thread_id

async def func1(num):
    start_time = time.strftime("%H:%M:%S")
    await asyncio.sleep(num)
    end_time = time.strftime("%H:%M:%S")
    
    print("{0} start_time: {1}, end_time: {2}, thread: {3}\n".format(num, start_time, end_time, get_thread_id()))
    
def start_loop(new_loop):
    print("Set New Loop, Thread:{0}".format(get_thread_id()))
    
    asyncio.set_event_loop(new_loop)
    
    new_loop.run_forever()

def test_main():
    
    loop1 = asyncio.new_event_loop()
    thread1 = threading.Thread(target=start_loop, args=(loop1, ))
    thread1.start()
    asyncio.run_coroutine_threadsafe(func1(1), loop1)
    asyncio.run_coroutine_threadsafe(func1(2), loop1)
    asyncio.run_coroutine_threadsafe(func1(3), loop1)
    
    loop2 = asyncio.new_event_loop()
    thread2 = threading.Thread(target=start_loop, args=(loop2, ))
    thread2.start()
    asyncio.run_coroutine_threadsafe(func1(1), loop2)
    asyncio.run_coroutine_threadsafe(func1(2), loop2)
    asyncio.run_coroutine_threadsafe(func1(3), loop2)
    
    
    print ("\n-------- Set Over! ----------!")
    


if __name__ == '__main__':
    test_main()