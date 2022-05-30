import asyncio

# 测试超时 协程设置

async def func1():
    print("func1 start!")
    
    await asyncio.sleep(3.6)
    
    print("func1 end!")
  
  
async def func2(a, b):
    print("func2 start!")
    await asyncio.sleep(3)
    print("func2 end!")
      

async def time_out_main():
    try:
        await asyncio.wait_for(func1(), timeout=4)
    except asyncio.TimeoutError:
        print('超时了！')
        
def test_time_out():
    asyncio.run(time_out_main())
    

    return a+b

def func2_call_back(future):
    print("func2_call_back: {0}".format(future.result()))

def test_call_back():
    loop = asyncio.get_event_loop()
    
    task = asyncio.ensure_future(func2(10, 5))
    task.add_done_callback(func2_call_back)
    
    
    loop.run_until_complete(task)
    
    # asyncio.run(task)
    
    


if __name__ == "__main__":
    # test_time_out()
    
    test_call_back()