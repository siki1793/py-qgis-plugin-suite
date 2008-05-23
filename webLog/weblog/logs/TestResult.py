class TestResult(Result):
    #constructeur
    def __init__(self,testName,testDescription,resultBool=True,errorTestResultComments=ResultComment(),generalResultComments=ResultComment()):
        if((not isinstance(testName,basestring)) or (not isinstance(testDescription,basestring)) ):
             raise "Error : trying to initialize a 'TestResult' object with an object which is not of the 'basestring' type"        
        if(not isinstance(resultBool,bool)):
            raise "Error : trying to add a 'resultBool' object which is not of the 'Bool' type"            
        if( (not isinstance(errorTestResultComments,ResultComment)) or (not isinstance(generalResultComments,ResultComment))):
            raise "Error : trying to initialize a 'TestResult' object with an object which is not of the 'ResultComment' type"        
        self.testName = testName
        self.testDescription = testDescription
        Result.__init__(self,resultBool,errorTestResultComments,generalResultComments)
    
    def getTestName(self):
        return self.testName
    
    def getTestDescription(self):
        return self.testDescription
         
    # add self + an Result
    # add the ResultComment of the Result only if it is False
    def __add__(self,result):
        if(not (isinstance(result,Result) or isinstance(result,TestResult)) ):
           raise "Error : trying to add an object which is not of the 'Result' or 'TestResult' type"
        _result = Result.__add__(self, result)        
        return TestResult(self.getTestName(),self.getTestDescription(),_result.getResultBool(),_result.getErrorResultComment(),_result.getGeneralResultComments())    
    