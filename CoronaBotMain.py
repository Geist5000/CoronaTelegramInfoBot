import asyncio
import schedule
from bot import CoronaBot
import os
from dotenv import load_dotenv
load_dotenv()

loop = asyncio.get_event_loop()



api_id = os.getenv("APIID")
api_hash = os.getenv("APIHASH")
token = os.getenv("BOTTOKEN")
bot = CoronaBot(api_id, api_hash)
    
async def main():
    
    asyncio.create_task(sheduleMessagesAsync())
    await bot.start(token)
    print("started")
    await bot.runUntilDisconnect()
    
def sendUpdate():
    asyncio.create_task(bot.sendUpdateToAll())
    
async def sheduleMessagesAsync():
    schedule.every().day.at("09:00").do(sendUpdate)
    while 1:
        schedule.run_pending()
        await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt as interrupt:
        print("Keyboard Interrupt")
        pass
