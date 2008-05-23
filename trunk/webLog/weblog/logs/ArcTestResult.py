class ArTestResult:
    def __init__(self,arTestResultName,arTestResultDescription):
        if((not isinstance(arTestResultName,basestring)) or (not isinstance(arTestResultDescription,basestring)) ):
             raise "Error : trying to initialize a 'ArTestResult' object with an object which is not of the 'basestring' type"        
         
        self.arTestResultList = []
        self.arTestResultName = arTestResultName
        print "* "+arTestResultName
        self.arTestResultDescription = arTestResultDescription
    
    def addTestResult(self,testResult):
        if(not isinstance(testResult,TestResult)):
           raise "Error : trying to add an object which is not of the 'TestResult' type"
        self.arTestResultList.append(testResult)
        
    def getName(self):
        return self.arTestResultName
    
    def getDescription(self):
        return self.arTestResultDescription
    
    def getTestResultList(self):
        return self.arTestResultList
    
    def getResultBool(self):
        resultBool = True
        for testResult in self.getTestResultList():
            resultBool = resultBool and testResult.getResultBool()            
        return resultBool