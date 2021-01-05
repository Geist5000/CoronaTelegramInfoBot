import requests
from datetime import datetime
from Regions import *
from urllib.parse import quote
from DataSources import DataSource,Region


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

    def getPossibleNameForRegionType(self,region):
        if(region.type == "Stadtkreis"):        