from asyncio.events import get_event_loop
from telethon.events.newmessage import NewMessage
from telethon.sync import TelegramClient 
from telethon.tl.types import InputPeerUser, KeyboardButton 
from telethon import TelegramClient, events
from telethon.errors import UserIsBlockedError
from UserStore import UserStore
from DataStore import *

import asyncio

class CoronaBot(object):
    def __init__(self,apiId,apiHash) -> None:
        self.bot = TelegramClient('CoronaWHVBot', apiId, apiHash)
        self.bot.add_event_handler(self.onStartMessage,events.NewMessage(pattern="/start"))
        self.bot.add_event_handler(self.onRegularMessage,events.NewMessage(pattern="^(?!/start.*$).*"))
        self.userStore = UserStore()
        self.dataStoreProvider = RegionSourceProvider()

    def __del__(self):
        self.stop()
        
    async def start(self,token):
        return await self.bot.start(bot_token=token)

    async def stop(self):
        self.userStore.close()
        asyncio.get_running_loop().run_until_complete(self.bot.disconnect())
        print("Bot stoped and database closed")
    
    async def onStartMessage(self,event):
        sender = event.input_sender
        try:    
            self.userStore.addUserToDB(sender.user_id,sender.access_hash)
            print("added user")
            await event.respond("Du wurdest erfolgreich hinzugefügt. Du kriegst von mir ab jetzt jeden Morgen um 09:00 eine Übersicht der aktuellen Lage",buttons=getResponseKeyboard())
        except:
            await event.respond("Irgendwas hat nicht funktioniert! Probiere nochmal \"/start\" oder kontaktiere den Admin")
            print("saving went wrong")

    async def onRegularMessage(self,event):
        sender = event.input_sender
        databaseUser = self.userStore.getUser(sender.user_id,sender.access_hash)
        if(databaseUser[2] == None):
            await self.tryAddRegionType(event,databaseUser)
        elif(databaseUser[3] == None):
            await self.tryAddRegionName(event,databaseUser)
        else:
            await event.reply("Ich weiß nicht was ich tun soll!")

        
    async def tryAddRegionType(self,event,databaseUser):
        pass

    async def tryAddRegionName(self,event,databaseUser):
        pass

    async def sendUpdateToAll(self):
        print("Sending Number Update to all users") 
        users = filter(lambda u: u[2]  != None and u[3] != None,self.userStore.getAllActiveUsers())
        for user in users:
            peer = InputPeerUser(user[0],user[1])
            message = getMessage(self.dataStoreProvider.getSourceFromRegion(Region(user[2],user[3])))
            try:
                await self.bot.send_message(peer,message,parse_mode="html")
            except UserIsBlockedError:
                self.userStore.removeUserFromDB(user[0])
        print("all messages send")

    async def runUntilDisconnect(self):
        return await self.bot.run_until_disconnected()

def getResponseKeyboard():
    return [[KeyboardButton("Bundesland"),KeyboardButton("Landkreis"),KeyboardButton("Kreisfreie Stadt")]]