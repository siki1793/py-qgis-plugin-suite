#Le HTML Handler pour les tests
class HTMLArTestResultsHandler:
    def __init__(self):                
        date = datetime.datetime.now().strftime("(%a) %d/%m/%Y %Hh%Mmin %Ssec")
        pageTitle =  "Execution : "+date
        self.pageHead = part('head')
        self.pageHead.addPart('title', content=pageTitle)
        
        #Initialisation CSS        
        cssStyle = "BODY { font-family:arial; font-size:11pt; }"
        cssStyle += "\n"
        cssStyle += "H1 {font: 30px Arial;font-weight: bold;color=black;}"
        cssStyle += "\n"
        cssStyle += "H2 {font: 24px Arial;font-weight: bold;color=black;}"
        cssStyle += "\n"
        cssStyle += "H3 {font: 20px Arial;font-weight: bold;color=black;}"
        cssStyle += "\n"
        cssStyle += "a.RESULT_OK { background-color: #409040; color: beige; }"
        cssStyle += "\n"
        cssStyle += "a.RESULT_BAD { background-color: #CC0033; color: beige; }"
        cssStyle += "\n"
        cssStyle += "TABLE.RESULT_TABLE { font-family:arial; font-size:10pt; width:800px; border-style:solid; border-color:black; border-width:1px; border-collapse:collapse; }"
        cssStyle += "\n"
        cssStyle += "TH.RESULT_HEADER { font-size:11pt; background-color:white; color:black; border-style:solid; border-width:1px; text-align:center; }"
        cssStyle += "\n"
        cssStyle += "TR.RESULT_ROW_OK {   background-color:#409040; }"
        cssStyle += "\n"
        cssStyle += "TR.RESULT_ROW_BAD {  background-color:#CC0033; }"
        cssStyle += "\n"
        cssStyle += "TD.RESULT_CELL { vertical-align:top; text-align:left; font-size:10pt; color:white; border-style:solid; border-width:1px; border-color:black; }"        
        self.pageHead.addPart('style', content=cssStyle)
        
        #Initialisation BODY
        self.pageBody = part('body')
        self.pageBody.addPart('h1', content="ARCHIVIDEO - RAPPORT D'EXECUTION",id="PageLinkUp")
        self.pageBody.addPart('p',content="Date : "+date)
        self.pageBody.addPart('hr')
        
        #Ajout sommaire qui sera complÃ©tÃ© plus tard...
        self.pageBody.addPart('h2',content="RÃ©sumÃ© des operations effectuÃ©es")
        self.summary = part('div')
        self.pageBody.addPiece(self.summary)
        self.pageBody.addPart('hr')
        
        #Initialisation liste des identifiants pour le sommaire
        self.idStringList = []
        self.idStringPrefix = "ArchiTest"
        self.idCount = 0
    
    #Returns prefix and number 'nb' as a String
    def __getIDString(self,prefix,nb):
        return prefix+str(nb)
    
    def __formatText(self,text):        
        maxCharactersOnALine = 60    
        sepList = ["\n"]
        splitText = string_multiSplit(text,sepList)                
        
        newText = ""
        for elem in splitText:
               elemSize = len(elem)
               if((elemSize>0) and (elemSize<=maxCharactersOnALine)):
                   newText += elem + "<br>"
               else:
                   if(elemSize>0):
                       sepList2 = [" "]
                       splitElem = string_multiSplit(elem,sepList2)
                       
                       line = ""
                       for i in range(len(splitElem)):
                           lineSize = len(line)
                           
                           isLastWord = (i==len(splitElem)-1)                           
                           word = splitElem[i]                           
                           if(not isLastWord):
                               word += " "
                           
                           wordSize = len(word)                           
                           
                           #si le mot lui-mÃªme est plus grand que la limite
                           if(wordSize>maxCharactersOnALine):                                  
                               firstCharIndex = 0
                               lastCharIndex = firstCharIndex+min(maxCharactersOnALine-lineSize,wordSize-firstCharIndex)
                               while(firstCharIndex<wordSize):                                                                      
                                   line += word[firstCharIndex:lastCharIndex+1]
                                   
                                   if(len(line)>=maxCharactersOnALine):
                                       newText += line + "<br>"
                                       line = ""
                                       lineSize = len(line)                                 
                                   
                                   firstCharIndex = lastCharIndex+1
                                   lastCharIndex = firstCharIndex+min(maxCharactersOnALine-lineSize,wordSize-firstCharIndex)
                                   
                               
                           else:
                               #si le mot passe sur la ligne
                               if(lineSize+wordSize<=maxCharactersOnALine):
                                   line += word
                               else:
                                  if( (len(line)>0) and (line!=" ")):
                                      newText += line + "<br>"
                                  line = word
                                  
                       if(len(line)>0):
                           newText += line + "<br>"
        
        return newText
    
    #ConsidÃ©rÃ© comme un ArTestResult avec seulemen un titre + description
    def addTestResult(self,testResult):
        if(not isinstance(testResult,TestResult)):
           raise "Error : trying to add an object which is not of the 'TestResult' type"       
        
        arTestResult = ArTestResult(testResult.getTestName(),testResult.getTestDescription())        
        arTestResult.addTestResult(testResult)
        self.addArTestResult(arTestResult)
    
    #ConsidÃ©rÃ© comme plusieurs TestResults + un titre + description
    def addArTestResult(self,arTestResult,prefix="",count=-1):
        if(not isinstance(arTestResult,ArTestResult)):
           raise "Error : trying to add an object which is not of the 'ArTestResult' type"               
       
        if( (prefix=="") or (count==-1) ):
           idString = self.__getIDString(self.idStringPrefix,self.idCount)
           self.idCount += 1
        else:
            idString = self.__getIDString(prefix,count)
        
        arTestResultName = arTestResult.getName()        
        arTestResultBool = arTestResult.getResultBool()
        self.idStringList.append([idString,arTestResultName,arTestResultBool,0])
        self.pageBody.addPart('h3',content=arTestResultName,id=idString)
        
        self.pageBody.addPart('p',content="Description de l'operation :<br>"+arTestResult.getDescription().replace("\n","<br>"))
        
        testResultList = arTestResult.getTestResultList()
        if(len(testResultList)>0):
            testArray = table(style="RESULT_TABLE")
            testArray.addRow(["RESULTAT","OPERATION","DESCRIPTION","DETAILS CONCERNANT L'ERREUR","DIVERS"],celltype="th",cellclass="RESULT_HEADER")
            
            for testResult in testResultList:       
                
                testRow = []
                
                result = testResult.getResultBool()
                
                if(result):
                    resultString = "OK"
                    rowStyle = "RESULT_ROW_OK"
                else:                                
                    resultString = "ECHEC"
                    rowStyle = "RESULT_ROW_BAD"
                testRow.append(resultString)
                
                testRow.append(self.__formatText(testResult.getTestName()))
                testRow.append(self.__formatText(testResult.getTestDescription()))     
    
                errorCommentString = ""        
                if(not result):
                    errorCommentList = testResult.getErrorResultComment().getCommentList()
                    for errorComment in errorCommentList:
                        errorCommentString += errorComment+"\n"
                else:
                    errorCommentString += "/"
                testRow.append(self.__formatText(errorCommentString))
                   
                generalCommentString = "" 
                if(not testResult.getGeneralResultComments().isEmpty()):
                    generalCommentList = testResult.getGeneralResultComments().getCommentList()
                    for generalComment in generalCommentList:
                        generalCommentString += generalComment+"\n"
                else:
                    generalCommentString += "/"                    
                testRow.append(self.__formatText(generalCommentString))
                
                testArray.addRow(testRow,cellclass="RESULT_CELL",style=rowStyle,cellAttributes={"NOWRAP":"1"})
                
            self.pageBody.addPiece(testArray)
            
        self.pageBody.addPart('p')        
        self.pageBody.addPart('a',content="> Haut de la page",attributes={"HREF":"#PageLinkUp"})
        self.pageBody.addPart('p')
        self.pageBody.addPart('p')
        self.pageBody.addPart('p')
        self.pageBody.addPart('p')
        self.pageBody.addPart('p')
        


    def addArTestResultCollection(self,arTestResultCollection):
        if(not isinstance(arTestResultCollection,ArTestResultCollection)):
           raise "Error : trying to add an object which is not of the 'ArTestResultCollection' type"
        
        idString = self.__getIDString(self.idStringPrefix,self.idCount)
        self.idCount += 1
        
        arTestResultCollectionName = arTestResultCollection.getName()
        arTestResultCollectionResultBool = arTestResultCollection.getResultBool()
        nbSubTests = len(arTestResultCollection.getArTestResultList())
        self.idStringList.append([idString,arTestResultCollectionName,arTestResultCollectionResultBool,nbSubTests])
        self.pageBody.addPart('h2',content=arTestResultCollectionName,id=idString)
        self.pageBody.addPart('a',content="> Haut de la page",attributes={"HREF":"#PageLinkUp"})
        
        arTestResultList = arTestResultCollection.getArTestResultList()
        count = 0
        for arTestResult in arTestResultList:        
            self.addArTestResult(arTestResult,prefix=idString+"_",count=count)
            count += 1
 
    #outputFile must have been opened before
    def saveAsHTML(self, outputFile):
        fullPage = part('html')
        fullPage.addPiece(self.pageHead)
        
        #CrÃ©ation sommaire
        #calcul de la position de chaque element dans le sommaire
        rankList = []
        for i in range(len(self.idStringList)):
            rankList.append(0) #initialisation
        
        for i in range(len(self.idStringList)):
            [id,testname,result,nbSubTests] = self.idStringList[i]
            
            if(nbSubTests>0):
                j=1
                while( (j<=nbSubTests) and (i+j<len(rankList)) ):
                    rankList[i+j] += 1
                    j += 1            
        
        #Calcul sommaire
        summaryPart = part("div")
        for i in range(len(self.idStringList)):
            [id,testname,result,nbSubTests] = self.idStringList[i]
            rank = rankList[i]
            
            
            if(result):
                cssLinkStyle = "RESULT_OK"
            else:
                cssLinkStyle = "RESULT_BAD"
            
            summaryLinkedList = linkedList(aclass=cssLinkStyle)
            summaryLinkedList.addLink(["#"+id,testname])
            
            decalage = part("p")
            decalage.addPiece(summaryLinkedList) 
            for j in range(rank):
                decalage2 = copy.deepcopy(decalage)
                decalage = linkedList()
                decalage.addPiece(decalage2)        

            summaryPart.addPiece(decalage)                    
        
        #Ajout du sommaire Ã  la page
        self.summary.addPiece(summaryPart)           
        
        fullPage.addPiece(self.pageBody)
        htmlCodeString = fullPage.make()        
        outputFile.write(htmlCodeString)