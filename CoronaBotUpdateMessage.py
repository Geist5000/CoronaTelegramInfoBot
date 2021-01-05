from bot import CoronaBot
import sys
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()



async def main(message):
    api_id = os.getenv("APIID")
    api_hash = os.getenv("APIHASH")
    token = os.getenv("BOTTOKEN")
    bot = CoronaBot(api_id, api_hash)

    await bot.start(token)
    await bot.sendMessageToAll(message)
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    argCount = len(sys.argv)
    if(argCount == 2):
        filePath = sys.argv[1]
        message = ""
        with open(filePath) as f:
            message = "".join(f.readlines())
        loop.run_until_complete(main(message))

        
        
        