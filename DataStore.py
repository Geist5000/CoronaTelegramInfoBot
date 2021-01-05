import requests
from datetime import datetime,timedelta
from urllib.parse import quote

from telethon.client import updates

class Region(object):
    _types = ["Bundesland","Landkreis","Stadtkreis"]

    def __init__(self,t,name):
        if t not in self._types:
            raise Exception("not a valid type")
        self.type = t
        self.name = name
    def __str__(self) -> str:
        return self.name
    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.type == other.type and self.name == other.name
        else:
            return False
    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)
    def __hash__(self) -> int:
        return hash((self.type,self.name))
        
        
        
class DataSource(object):

    def __init__(self,city:Region):
        self.city = city
    def getTotalCases(self):
        raise NotImplemented()
    def getReputitionOf7Days(self):
        raise NotImplemented()
    def getCurrentCases(self):
        raise NotImplemented()
    def getTotalDeaths(self):
         raise NotImplemented()
    def getRegion(self):
        return self.city
    def getLastUpdate(self):
        raise NotImplemented()
    def getSourceText(self):
        raise NotImplemented()
    def getLicenceText(self):
        raise NotImplemented()
    
        
class CitySource(DataSource):
    def __init__(self,city:Region):
        if(city.type !="Stadtkreis"):
            raise TypeError("Invalid city type")
        super().__init__(city)
        self.dataSource = r"https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query"
        self.source = r"https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0"
        self.licence = r"http://www.govdata.de/dl-de/by-2-0"
        self.data = None
        self.lastUpdate = None
        
    def getRawData(self):
        if(self.lastUpdate == None) or ((datetime.now() - self.lastUpdate).days >= 1):
            r = requests.get("{0:s}?f=json&returnGeometry=false&where={1:s}&outFields={2:s}".format(self.dataSource,quote(self.getWhereQuerry(),safe=','),",".join(self.getOutFields())))
            self.data = r.json()
            dateString = self.data["features"][0]["attributes"]["last_update"]
            self.lastUpdate = datetime.strptime(dateString,"%d.%m.%Y, %H:%M Uhr")
        return self.data
        
    def getProcessedData(self):
        return self.getRawData()["features"][0]["attributes"]

    def getReputitionOf7Days(self):
        return self.getProcessedData()["cases7_per_100k"]
    def getTotalCases(self):
        return self.getProcessedData()["cases"]
    def getTotalDeaths(self):
        return self.getProcessedData()["deaths"]
    def getLastUpdate(self):
        return self.getProcessedData()["last_update"]
    def getWhereQuerry(self):
        return "GEN = '{:s}'".format(self.city.name)
    def getOutFields(self):
        return ["GEN","last_update","cases7_per_100k","cases","deaths"]
    def getLicenceText(self):
        return "<a href=\"{:s}\">Robert Koch-Institut (RKI), dl-de/by-2-0</a>".format(self.licence)
    def getSourceText(self):
        return "<a href=\"{:s}\">Datensatz</a>".format(self.source)


class RegionSourceProvider(object):
    def __init__(self) -> None:
        self.sources = {}
    def getSourceFromRegion(self,region:Region):
        if region not in self.sources:

            if(region.type =="Stadtkreis"):
                self.sources[region] = CitySource(region)
        return self.sources[region]


class UpdateTextLine(object):


    def __init__(self,text:str,method) -> None:
        self.text = text
        self.method = method
    def getLineOrThrow(self,data:DataSource):
        
        return self.text.format(self.method(data) if self.method != None else "")


updateText = [
    UpdateTextLine("Die Aktuellen Corona Zahlen von {:s}\n", lambda source : str(source.getRegion()) ),
    UpdateTextLine("7-Tage-Inzidenz:   <b><u>{:.2f}</u></b>\n", lambda source : source.getReputitionOf7Days()),
    UpdateTextLine("Aktuelle Fälle:   <b><u>{:d}</u></b>\n", lambda source : source.getCurrentCases()),
    UpdateTextLine("Alle Fälle:   <b><u>{:d}</u></b>\n", lambda source : source.getTotalCases()),
    UpdateTextLine("Alle Tode:   <b><u>{:d}</u></b>\n", lambda source : source.getTotalDeaths()),
    UpdateTextLine("Pass auf dich auf\n\nLetze Aktualisierung: {:s}\n", lambda source : source.getLastUpdate()),
    UpdateTextLine("\n\nQuelle:\n{:s}\n", lambda source : source.getSourceText()),
    UpdateTextLine("Lizenz: {:s}", lambda source : source.getLicenceText())
]



def getMessage(data:DataSource):
    """get message for given dataSource"""
    message = ""
    for line in updateText:
        try:
            message += line.getLineOrThrow(data)
        except Exception as err:
            # print(err)
            pass
    return message

# DEBUG
if __name__ == "__main__":
    region = Region("Stadtkreis","Wilhelmshaven")
    provider = RegionSourceProvider()
    print(getMessage(provider.getSourceFromRegion(region)))