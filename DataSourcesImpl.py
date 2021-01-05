import requests
from datetime import datetime
from Regions import *
from urllib.parse import quote
from DataSources import DataSource,Region, getMessage


class DistrictSource(DataSource):
    def __init__(self,city:Region):
        if(city.type !="Landkreis"):
            raise TypeError("Invalid city type")
        self.city = city
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

class StateSource(DataSource):
    def __init__(self,state:Region):
        if(state.type !="Bundesland"):
            raise TypeError("Invalid city type")
        self.state = state
        super().__init__(state)
        self.dataSource = r"https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/Coronaf%C3%A4lle_in_den_Bundesl%C3%A4ndern/FeatureServer/0/query"
        self.source = r"https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/ef4b445a53c1406892257fe63129a8ea_0"
        self.licence = r"http://www.govdata.de/dl-de/by-2-0"
        self.data = None
        self.lastUpdate = None
        
    def getRawData(self):
        if(self.lastUpdate == None) or ((datetime.now() - self.lastUpdate).days >= 1):
            r = requests.get("{0:s}?f=json&returnGeometry=false&where={1:s}&outFields={2:s}".format(self.dataSource,quote(self.getWhereQuerry(),safe=','),",".join(self.getOutFields())))
            self.data = r.json()
            timestamp = self.data["features"][0]["attributes"]["Aktualisierung"]/1000
            self.lastUpdate = datetime.fromtimestamp(timestamp)
        return self.data
        
    def getProcessedData(self):
        return self.getRawData()["features"][0]["attributes"]

    def getReputitionOf7Days(self):
        return self.getProcessedData()["cases7_bl_per_100k"]
    def getTotalCases(self):
        return self.getProcessedData()["Fallzahl"]
    def getTotalDeaths(self):
        return self.getProcessedData()["Death"]
    def getLastUpdate(self):
        return self.lastUpdate.strftime("%d.%m.%Y, %H:%M Uhr")
    def getWhereQuerry(self):
        return "LAN_ew_GEN = '{:s}'".format(self.state.name)
    def getOutFields(self):
        return ["LAN_ew_GEN","Aktualisierung","cases7_bl_per_100k","Fallzahl","Death"]
    def getLicenceText(self):
        return "<a href=\"{:s}\">Robert Koch-Institut (RKI), dl-de/by-2-0</a>".format(self.licence)
    def getSourceText(self):
        return "<a href=\"{:s}\">Datensatz</a>".format(self.source)


class RegionSourceProvider(object):
    def __init__(self) -> None:
        self.sources = {}
    def getSourceFromRegion(self,region:Region):
        if region not in self.sources:

            if(region.type =="Landkreis"):
                self.sources[region] = DistrictSource(region)

            if(region.type == "Bundesland"):
                self.sources[region] = StateSource(region)

        return self.sources[region]

    def getPossibleNameForRegionType(self,region):
        if(region.type == "Landkreis"):
            return lk
        if(region.type == "Bundesland"):
            return bl

if(__name__ == "__main__"):
    source = StateSource(Region("Bundesland","Niedersachsen"))
    print(getMessage(source))