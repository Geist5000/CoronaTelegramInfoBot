import sqlite3

class UserStore(object):
    
    
    def __init__(self,fileName="users.db"):
        self.fileName = fileName
        self._db = sqlite3.connect(fileName)
        self._userTableName = "activeUsers"
        self._userColumn = "user_id"
        self._hashColumn = "access_hash"
        self._regionTypeColumn = "region_type"
        self._regionNameColumn = "region_name"
        self._c = self._db.cursor()
        self._c.execute("CREATE TABLE IF NOT EXISTS `{0:s}`({1:s} INTEGER NOT NULL Primary Key,{2:s} INTEGER NOT NULL,{3:s} VARCHAR(20), {4:s} VARCHAR(40));".format(self._userTableName,self._userColumn,self._hashColumn,self._regionTypeColumn,self._regionNameColumn))
        self.save()
        
    def addUserToDB(self,id,hash):
        self._c.execute("REPLACE INTO `%s` (%s,%s) VALUES (?,?)"%(self._userTableName,self._userColumn,self._hashColumn), (id,hash))
        self.save()
        
    def removeUserFromDB(self,id):
        self._c.execute("DELETE FROM `%s` WHERE %s=?;"%(self._userTableName,self._userColumn), (id))
        self.save()

    def setRegionTypeOfUser(self,id,hash,t):
        self._c.execute("UPDATE `%s` SET `%s`=? WHERE %s;"%(self._userTableName,self._regionTypeColumn,self.getUserCondition()) , (t,id,hash))
        self.save()

    def setRegionNameOfUser(self,id,hash,name):
        self._c.execute("UPDATE `%s` SET `%s`=? WHERE %s;"%(self._userTableName,self._regionNameColumn,self.getUserCondition()) , (name,id,hash))
        self.save()


    def setRegionOfUser(self,id,hash,t,name):
        self._c.execute("UPDATE `%s` SET `%s`=?,`%s`=? WHERE %s;"%(self._userTableName,self._regionTypeColumn,self._regionNameColumn,self.getUserCondition()),(t,name,id,hash))
        self.save()

    def getUser(self,id,hash):
        self._c.execute("SELECT * FROM `%s` WHERE %s"%(self._userTableName,self.getUserCondition()),(id,hash))
        return self._c.fetchone()

    def getUserCondition(self):
        return "`%s`=? AND `%s`=?"%(self._userColumn,self._hashColumn)
    def removeRegionNameOfUser(self,id,hash):
        self.setRegionOfUser(id,hash,None,None)
        
    def getAllActiveUsers(self):
        c = self._db.cursor()
        c.execute("SELECT * FROM `%s`"%(self._userTableName))
        return c.fetchall()
        
    def save(self):
        self._db.commit()
    def close(self):
        self._db.close()