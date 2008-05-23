class Result:
    
    #constructeur    
    def __init__(self,resultBool=True,errorResultComments=ResultComment(),generalResultComments=ResultComment()):
        if(not isinstance(resultBool,bool)):
            raise "Error : trying to add a 'resultBool' object which is not of the 'Bool' type"
        
        if( (not isinstance(errorResultComments,ResultComment)) or (not isinstance(generalResultComments,ResultComment))):
           raise "Error : trying to initialize a 'Result' object with an object which is not of the 'ResultComment' type"
        self.resultBool = resultBool
        
        self.generalResultComments = ResultComment()
        self.generalResultComments += generalResultComments
        
        self.errorResultComments = ResultComment()
        if(not resultBool):
            self.errorResultComments += errorResultComments
     
    def getResultBool(self):
        return self.resultBool
    
    def setResultBool(self,boolValue):
        if(not isinstance(boolValue,bool)):
            raise "Error : trying to add a 'boolValue' object which is not of the 'Bool' type"            
        self.resultBool = boolValue
        
    def addResultBool(self,boolValue):
        if(not isinstance(boolValue,bool)):
            raise "Error : trying to add a 'boolValue' object which is not of the 'Bool' type"            
        self.resultBool = self.resultBool and boolValue
    
    def getErrorResultComment(self):
        return self.errorResultComments
    
    def addErrorResultComment(self,errorResultComment):
        if(not isinstance(errorResultComment,ResultComment)):
           raise "Error : trying to add an object which is not of the 'ResultComment' type"
        self.errorResultComments+=errorResultComment
    
    def getGeneralResultComments(self):
        return self.generalResultComments
    
    def addGeneralResultComments(self,generalResultComments):
        if(not isinstance(generalResultComments,ResultComment)):
           raise "Error : trying to add an object which is not of the 'ResultComment' type"
        self.generalResultComments+=generalResultComments
    
    # add self + an Result
    # add the ResultComment of the Result only if it is False
    def __add__(self,result):
        if(not isinstance(result,Result)):
           raise "Error : trying to add an object which is not of the 'Result' type"
        _resultBool = self.getResultBool() and result.getResultBool()
        
        _errorResultComments = self.getErrorResultComment()
        if(not result.getResultBool()):
            _errorResultComments += result.getErrorResultComment()
            
        _generalResultComments = self.getGeneralResultComments()
        _generalResultComments += result.getGeneralResultComments()
              
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

            
        return Result(_resultBool,_errorResultComments,_generalResultComments)
        