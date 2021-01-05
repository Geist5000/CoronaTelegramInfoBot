class Region(object):
    types = ["Bundesland","Landkreis"]

    def __init__(self,t,name):
        if t not in self.types:
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