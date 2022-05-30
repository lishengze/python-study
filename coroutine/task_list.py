import asyncio
import time

async def task1():
    # while(True):
        start_time = time.strftime('%H:%M:%S')
    
        await asyncio.sleep(3)
        
        await asyncio.sleep(2)
        
        # time.sleep(3)

        end_time = time.strftime('%H:%M:%S')
        
        print("[1] start_time: {0}, end_time: {1}".format(start_time, end_time))
    
async def task2():
    # while(True):
        start_time =time.strftime('%H:%M:%S')
    
        # await asyncio.sleep(3)
        
        # time.sleep(3)

        end_time = time.strftime('%H:%M:%S')
        
        print("[2] start_time: {0}, end_time: {1}".format(start_time, end_time))    
    
async def task3():
    while(True):
        start_time =time.strftime('%H:%M:%S')
    
        await asyncio.sleep(3)

        end_time = time.strftime('%H:%M:%S')
        
        print("[3] start_time: {0}, end_time: {1}".format(start_time, end_time))       
        
async def task4():
        start_time =time.strftime('%H:%M:%S')
    
        await task1()
        
        await task2()

        end_time = time.strftime('%H:%M:%S')
        
        print("[3] start_time: {0}, end_time: {1}".format(start_time, end_time))         
    
def test_task():
    task_loop = asyncio.get_event_loop()
    # task_list = [task4()]
    
    task_list = [task1()]
    
    start_time = time.time()
    
    coroutine_tasks = asyncio.wait(task_list)
    
    task_loop.run_until_complete(coroutine_tasks)
    
    end_time = time.time()
    print("Cost: %d 秒"% (end_time - start_time))
    

if __name__ == "__main__":
    test_task()
    pass