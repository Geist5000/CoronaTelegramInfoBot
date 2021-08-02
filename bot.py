from reportlab.lib.utils import datareader
from telethon.sync import TelegramClient
from telethon.tl.custom import Button
from telethon.tl.types import InputPeerUser
from telethon import TelegramClient, events
from telethon.errors import UserIsBlockedError
from UserStore import UserStore
from DataSources import *
from DataSourcesImpl import RegionSourceProvider
import asyncio
import difflib


class CoronaBot(object):
    def __init__(self, apiId, apiHash) -> None:
        self.bot = TelegramClient('CoronaWHVBot', apiId, apiHash)
        self.bot.add_event_handler(self.onStartMessage, events.NewMessage(pattern="/start"))
        self.bot.add_event_handler(self.onStopMessage, events.NewMessage(pattern="/stop"))
        self.bot.add_event_handler(self.onRegionResetMessage, events.NewMessage(pattern="/resetRegion"))
        self.bot.add_event_handler(self.onFastInfoMessage, events.NewMessage(pattern="/check"))
        self.bot.add_event_handler(self.onRegularMessage,
                                   events.NewMessage(pattern="^(?!(/start|/stop|/resetRegion|/check).*$).*"))
        self.userStore = UserStore()
        self.dataStoreProvider = RegionSourceProvider()

        self.fastInfoRequests = {}

    def __del__(self):
        self.stop()

    async def start(self, token):
        return await self.bot.start(bot_token=token)

    async def stop(self):
        self.userStore.close()
        asyncio.get_running_loop().run_until_complete(self.bot.disconnect())
        print("Bot stoped and database closed")

    async def onStartMessage(self, event):
        sender = event.input_sender
        try:
            print(self.userStore.getUser(sender.user_id, sender.access_hash))
            self.userStore.addUserToDB(sender.user_id, sender.access_hash)
            print("added user")
            await event.respond(
                "Für welches Gebiet willst du jeden Morgen um 09:00 Nachrichten erhalten?\n\nBitte gebe zunächst die Art der Region an!",
                buttons=getRegionTypeKeyboard())
        except Exception as e:
            await event.respond(
                "Irgendwas hat nicht funktioniert! Probiere nochmal \"/start\" oder kontaktiere den Admin",
                buttons=getDisabledKeyboard())
            print("adding went wrong", e)

    async def onFastInfoMessage(self, event):
        try:
            self.fastInfoRequests[event.input_sender.user_id] = None
            await event.respond("Bitte gebe zunächst die Art der Region an!", buttons=getRegionTypeKeyboard())
        except Exception as e:
            await event.respond(
                "Irgendwas hat nicht funktioniert! Probiere nochmal \"/info\" oder kontaktiere den Admin",
                buttons=getDisabledKeyboard())
            print("fast info went wrong", e)

    async def onStopMessage(self, event):
        sender = event.input_sender
        try:
            self.userStore.removeUserFromDB(sender.user_id, sender.access_hash)
            print("removed user")
            await event.respond("Du wurdest erfolgreich entfernt, du wurst nun keine Nachrichten mehr erhalten!",
                                buttons=getDisabledKeyboard())
        except Exception as e:
            await event.respond("Das entfernen hat nicht funktioniert. Du wirst weiterhin Nachrichten erhalten!",
                                buttons=getDefaultKeyboard())
            print("deleting went wrong!", e)

    async def onRegionResetMessage(self, event):
        sender = event.input_sender
        try:
            self.userStore.removeRegionOfUser(sender.user_id, sender.access_hash)
            print("removed user")
            await event.respond(
                "Deine Region wurde erfolgreich entfernt. Für welche Region willst du ab jetzt Nachrichten erhalten?\n\nBitte gebe zunächst die Art der Region an!",
                buttons=getRegionTypeKeyboard())
        except Exception as e:
            await event.respond("Das entfernen hat nicht funktioniert. Du wirst weiterhin Nachrichten erhalten!",
                                buttons=getDefaultKeyboard())

    async def onRegularMessage(self, event):
        sender = event.input_sender
        databaseUser = self.userStore.getUser(sender.user_id, sender.access_hash)
        if (databaseUser[2] == None):
            await self.tryAddRegionType(event, databaseUser)
        elif (databaseUser[3] == None):
            await self.tryAddRegionName(event, databaseUser)
        elif (sender.user_id in self.fastInfoRequests.keys()):
            type = self.fastInfoRequests[sender.user_id]
            m = event.message.message
            if (type is None):

                if (self.getRegionType(m) is not None):
                    self.fastInfoRequests[sender.user_id] = m
                    await event.respond("Bitte gebe nun den Namen ein!", buttons=getDisabledKeyboard())
                else:
                    await event.respond("Das war kein erlaubte Regionsart!", buttons=getRegionTypeKeyboard())
            else:
                hasMatch, possibleNames = self.getRegionNameForType(databaseUser[2], m)
                if (hasMatch):
                    try:
                        await self.sendUpdateToUser(sender, self.fastInfoRequests[sender.user_id], possibleNames)
                    except:
                        pass
                else:
                    closeMatches = getCloseRegionNamesFromList(m, possibleNames)
                    me, bs = getRegionNameSuggestionMessage(closeMatches)
                    await event.respond(me, buttons=bs)
        else:
            await event.reply("Ich weiß nicht was ich tun soll!")

    def getRegionType(self, regionName):
        return regionName if any(map(lambda b: b.button.text == regionName, flatten(getRegionTypeKeyboard()))) else None

    async def tryAddRegionType(self, event, databaseUser):
        regionType = event.message.message
        isRegionType = self.getRegionType(regionType)
        if (None is not isRegionType):
            await event.respond("Das war kein erlaubte Regionsart!", buttons=getRegionTypeKeyboard())
        else:
            try:
                self.userStore.setRegionTypeOfUser(databaseUser[0], databaseUser[1], regionType)
                await event.respond("Schreibe jetzt bitte den Namen der Region!", buttons=Button.clear())
            except Exception as e:
                print("region type saving failed", e)
                await event.respond(
                    "Beim Speichern ist etwas schief gelaufen, versuche es nochmal oder kontaktiere den Admin")

    def getRegionNameForType(self, regionType, regionName):
        region = Region(regionType, None)
        possibleNames = [n.lower() for n in self.dataStoreProvider.getPossibleNameForRegionType(region)]
        if (regionName.lower() in possibleNames):
            return True, regionName
        else:
            return False, possibleNames

    async def tryAddRegionName(self, event, databaseUser):
        name = event.message.message
        hasMatch, possibleNames = self.getRegionNameForType(databaseUser[2])
        if (hasMatch):
            await event.respond(
                "Alles klar, ab jetzt bekommst du jeden Morgen um 09:00 eine Nachricht über die aktuelle Lage!",
                buttons=getDefaultKeyboard())
            self.userStore.setRegionNameOfUser(databaseUser[0], databaseUser[1], name)
        else:
            closeMatches = getCloseRegionNamesFromList(name, possibleNames)
            me, bs = getRegionNameSuggestionMessage(closeMatches)
            await event.respond(me, buttons=bs)

    async def sendMessageToAll(self, message):
        users = self.userStore.getAllActiveUsers()
        for u in users:
            peer = InputPeerUser(u[0], u[1])
            try:
                await self.bot.send_message(peer, message, parse_mode="html")
            except UserIsBlockedError:
                self.userStore.removeUserFromDB(u[0], u[1])

    async def sendUpdateToUser(self, peer, regionType, regionName):
        if (regionType) and (regionName):
            message = getMessage(self.dataStoreProvider.getSourceFromRegion(Region(regionType, regionName)))
            await self.bot.send_message(peer, message, parse_mode="html")

    async def sendUpdateToAll(self):
        print("Sending Number Update to all users")
        users = filter(lambda u: u[2] != None and u[3] != None, self.userStore.getAllActiveUsers())
        for user in users:
            peer = InputPeerUser(user[0], user[1])
            try:
                await self.sendUpdateToUser(peer, user[2], user[3])
            except UserIsBlockedError:
                self.userStore.removeUserFromDB(user[0], user[1])
            except:
                pass

        print("all messages send")

    async def runUntilDisconnect(self):
        return await self.bot.run_until_disconnected()


def getRegionTypeKeyboard():
    return getKeyboardFromList(Region.types)


def getDefaultKeyboard():
    return [[Button.text("/resetRegion"), Button.text("/stop"), Button.text("/check")]]


def getDisabledKeyboard():
    return [[Button.text("/start")]]  #


def getKeyboardFromList(l):
    return [list(map(lambda t: Button.text(t), l))]


def getRegionNameSuggestionMessage(regionnames):
    me = "Ich habe diesen Ort nicht gefunden!"
    bs = Button.clear()
    if (len(regionnames) > 0):
        bs = getKeyboardFromList(map(lambda n: n.capitalize(), regionnames))
        me += "\n\nMeinst du vielleicht:\n"
        for m in regionnames:
            me += " - %s\n" % (m.capitalize())
    return me, bs


def getCloseRegionNamesFromList(regionName, namesList):
    return list(difflib.get_close_matches(regionName, namesList, n=5))


def flatten(lst):
    for item in lst:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item
