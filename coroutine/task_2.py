import asyncio

# 测试超时 协程设置

async def func1():
    print("func1 start!")
    
    await asyncio.sleep(3.6)
    
    print("func1 end!")
    

async def time_out_main():
    try:
        await asyncio.wait_for(func1(), timeout=4)
    except asyncio.TimeoutError:
        print('超时了！')
        
def test_time_out():
    asyncio.run(time_out_main())

if __name__ == "__main__":
    test_time_out()