class ArTestResultCollection:
    def __init__(self,arTestResultCollectionName):
        if(not isinstance(arTestResultCollectionName,basestring)):
             raise "Error : trying to initialize a 'arTestResultCollectionName' object with an object which is not of the 'basestring' type"                        
        self.arTestResultCollectionList = []
        self.arTestResultCollectionName = arTestResultCollectionName
    
    def addArTestResult(self,arTestResult):
        if(not isinstance(arTestResult,ArTestResult)):
           raise "Error : trying to add an object which is not of the 'ArTestResult' type"        
        self.arTestResultCollectionList.append(arTestResult)
        
    def mergeArTestResultCollection(self,arTestResultCollection):
        if(not isinstance(arTestResultCollection,ArTestResultCollection)):
           raise "Error : trying to merge an object which is not of the 'ArTestResultCollection' type"
        arTestResultCollectionList = arTestResultCollection.getArTestResultList()
        for arTestResult in arTestResultCollectionList:
            self.addArTestResult(arTestResult)
        
    def getName(self):
        return self.arTestResultCollectionName    
    
    def getArTestResultNamesList(self):
        namesList = []
        for arTestResult in self.getArTestResultList():
            namesList.append(arTestResult.getName())
        return namesList
    
    def getArTestResultList(self):
        return self.arTestResultCollectionList
    
    def getResultBool(self):
        resultBool = True
        for arTestResult in self.getArTestResultList():
            resultBool = resultBool and arTestResult.getResultBool()            
        return resultBool