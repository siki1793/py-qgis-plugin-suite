#!/usr/bin/env python
# -*- coding: iso-8859-1 -*- 

#makeHTML.py version 0.8 May 1, 2005 Jerry Stratton
import datetime
import os, sys
import string
import re
import getopt
import os.path
import glob
import copy
import shutil
import gdal
import math
import datetime
#basic parts
class part:
    def __init__(self, code="p", content=None, style=None, id=None, attributes=None):
        self.style = style
        self.id=id
        self.pieces = []
        self.code = code
        if attributes == None:
            self.attributes = {}
        else:
            self.attributes = attributes
        if isinstance(content, list):
            self.addPieces(content)
        elif content != None:
            self.addPiece(content)
    
    def __len__(self):
        return len(self.pieces)

    def addAttribute(self, attributename, attributevalue):
        self.attributes[attributename] = attributevalue

    def addPart(self, code='p', content=None, style=None, id=None, attributes=None):
        newPart = self.makePart(code, content, style, id, attributes)
        self.addPiece(newPart)

    def addPiece(self, thePart):
        self.pieces.append(thePart)
    
    def addPieces(self, theParts):
        if theParts != None:
            if isinstance(theParts, list):
                for part in theParts:
                    self.addPiece(part)
            else:
                self.addPiece(theParts)
    
    def insertPart(self, code='p', content=None, style=None, id=None, attributes=None):
        newPart = self.makePart(code, content, style, id, attributes)
        self.insertPiece(newPart)
        
    def insertPiece(self, thePart):
        self.pieces.insert(0, thePart)

    def make(self, tab="\t"):
        startHTML = '<' + self.code
        
        if (self.attributes):
            for attribute in self.attributes:
                content = self.attributes[attribute]
                if content == None:
                    startHTML += ' ' + attribute
                else:
                    startHTML += ' ' + attribute + '="' + str(content) + '"'
    
        if (self.style):
            startHTML += ' class="' + self.style + '"'
        
        if (self.id):
            startHTML += ' id="' + self.id + '"'

        if self.pieces:
            startHTML += '>'
            
            partItems = [startHTML]
            
            if len(self.pieces) > 1:
                sep = "\n" + tab
                finalSep = sep[:-1]
                newtab = tab + "\t"
            else:
                newtab = tab
                sep = ""
                finalSep = ""
            
            for piece in self.pieces:
                if ( isinstance(piece, str) or isinstance(piece,unicode) ):
                    partItems.append(str(piece))
                elif isinstance(piece, int) or isinstance(piece, float):
                    partItems.append(str(piece))
                elif piece == None:
                    partItems.append("")
                else:
                    partItems.append(piece.make(newtab))
        
            code = sep.join(partItems)
            code += finalSep + '</' + self.code + '>'
            return code
            
        else:
            startHTML += ' />'
            return startHTML
    
    def makePart(self, code='p', content=None, style=None, id=None, attributes=None):
        if content == None:
            newPart = part(code)
        else:
            newPart = part(code, content, style, id, attributes)

        return newPart

class snippet(part):
    def __init__(self, code="em", content=None, posttext=None, pretext=None, style=None, id=None, attributes=None):
        part.__init__(self, code, content, style, id, attributes)
        self.posttext = posttext
        self.pretext = pretext
    
    def make(self, tab=''):
        snippets = []

        if self.pretext:
            snippets.append(self.pretext)
        
        snippets.append(part.make(self, tab))
        
        if self.posttext:
            snippets.append(self.posttext)

        return "".join(snippets)

#common body parts

class head(part):
    def __init__(self, title=None):
        part.__init__(self, code="head")
        if title:
            self.addPiece(part("title", title))

class body(part):
    def __init__(self, title=None, style=None, id=None, attributes=None):
        part.__init__(self, code="body", style=style, id=id, attributes=attributes)
        if title:
            self.addPiece(headline(title, 1))

class page(part):
    def __init__(self, pieces=None, style=None, id=None, attributes=None):
        part.__init__(self, code="html", style=style, id=id, attributes=attributes)
        if isinstance(pieces, list):
            self.addPieces(pieces)
        elif isinstance(pieces, part):
            self.addPiece(pieces)

    def make(self, tab=''):
        pageContent = part.make(self)
        
        print 'Content-type: text/html'
        print ''

        print pageContent

class styleSheet(part):
    def __init__(self, sheet, media='all'):
        attributes = {}
        attributes['rel'] = "StyleSheet"
        attributes['href'] = sheet + '.css'
        attributes['type'] = "text/css"
        attributes['media'] = media
        part.__init__(self, code="link", attributes=attributes)


#paragraph level parts
class headline(part):
    def __init__(self, content, level=2, style=None, id=None, attributes=None):
        code = "h"+str(level)
        part.__init__(self, content=content, style=style, code=code, id=id, attributes=attributes)



#tables
class table(part):
    def __init__(self, rows=None, style=None, thStyle=None, tdStyle=None, trStyle=None, tdBlankStyle=None, firstRowHeader=None, firstColumnHeader=None, id=None, attributes=None):
        part.__init__(self, code="table", style=style, id=id, attributes=attributes)
        self.rowclass=trStyle
        self.cellclass=tdStyle
        self.cellheaderclass=thStyle
        self.cellblankclass=tdBlankStyle
        self.firstRowHeader=firstRowHeader
        self.firstColumnHeader=firstColumnHeader
        if rows:
            self.addRows(rows)

    def addRow(self, rowList, celltype=None, cellclass=None, attributes=None, style=None,cellAttributes=None):
        if cellclass==None:
            if self.firstRowHeader and len(self.pieces) == 0:
                celltype="th"
                cellclass=self.cellheaderclass
            else:
                cellclass=self.cellclass

        if style==None:
            style = self.rowclass

        newRow = tableRow(celltype, rowList, style, cellclass, self.firstColumnHeader, self.cellheaderclass, attributes=attributes,cellAttributes=cellAttributes)
        self.addPiece(newRow)
    
    def addRows(self, rows, cellclass=None, celltype=None, attributes=None):
        for row in rows:
            self.addRow(row)

    def columnCount(self):
        maxCount = 0
        for row in self.pieces:
            if isinstance(row, tableRow):
                colCount = row.columnCount()
                maxCount = max(maxCount, colCount)
        
        return maxCount

class tableByColumn(table):
    def __init__(self, columns=None, style=None, thStyle=None, tdStyle=None, trStyle=None, tdBlankStyle=None, firstRowHeader=None, firstColumnHeader=None, id=None, attributes=None):
        table.__init__(self, [], style, thStyle, tdStyle, trStyle, tdBlankStyle, firstRowHeader, firstColumnHeader, id, attributes)
        self.columns = []
        if columns:
            self.addColumns(columns)

    def addColumn(self, columnList, celltype=None, cellclass=None, attributes=None):
        if cellclass==None:
            if celltype == "th" or (self.firstColumnHeader and len(self.columns) == 0):
                celltype="th"
                cellclass=self.cellheaderclass
            else:
                cellclass=self.cellclass

        newColumn = tableColumn(columnList, celltype, cellclass, self.firstRowHeader, self.cellheaderclass, self.cellblankclass, attributes)
        self.columns.append(newColumn)

    def addColumns(self, columns, celltype=None, cellclass=None, attributes=None):
        for column in columns:
            self.addColumn(column)

    def addPiece(self, thePart):
        if isinstance(thePart, tableColumn):
            self.columns.append(thePart)
        else:
            part.addPiece(self, thePart)

    def make(self, tabs):
        rowCount = 0
        for column in self.columns:
            rowCount = max(rowCount, len(column.pieces))

        if rowCount:
            for cRow in range(rowCount):
                row = tableRow()
                for column in self.columns:
                    if cRow < len(column.pieces):
                        cell = column.pieces[cRow]
                    else:
                        cell = part("td")
                    row.addPiece(cell)
                
                self.addPiece(row)

        myPart = part.make(self, tabs)
        return myPart


class tableColumn(part):
    def __init__(self, column=None, celltype="td", cellclass=None, firstRowHeader=None, thStyle=None, tdBlankStyle=None, attributes=None):
        part.__init__(self, "column", style=cellclass, attributes=attributes)
        if celltype==None:
            self.celltype = "td"
        else:
            self.celltype=celltype
        
        self.firstRowHeader=firstRowHeader
        self.cellheaderclass=thStyle
        self.cellblankclass=tdBlankStyle
        
        if column:
            self.addCells(column)

    def addCell(self, cell=None, celltype=None, cellclass=None, id=None, attributes=None):
        if self.cellblankclass and (cell==None or cell==""):
            celltype="td"
            cellclass = self.cellblankclass
        elif self.firstRowHeader and len(self.pieces) == 0:
            celltype = "th"
            cellclass = self.cellheaderclass
        else:
            if celltype == None:
                celltype = self.celltype
            if cellclass == None:
                cellclass = self.style
        if cell == None:
            cell = ""
        
        tableCell = part(code=celltype, style=cellclass, content=cell, id=id, attributes=attributes)
        self.addPiece(tableCell)

    def addCells(self, column, celltype=None, cellclass=None,  attributes=None):
        for cell in column:
            self.addCell(cell, celltype, cellclass, attributes=attributes)
    
    def make(self):
        print "Problem: columns should never be requested to make themselves."
        print "Columns are not true html structures, and should only be added to tableByColumn parts."


class tableRow(part):
    def __init__(self, celltype="td", row=None, style=None, cellclass=None, firstColumnHeader=None, thStyle=None, id=None, attributes=None,cellAttributes=None):
        part.__init__(self, "tr", style=style, id=id, attributes=attributes)
        self.celltype=celltype
        self.cellclass=cellclass
        self.firstColumnHeader=firstColumnHeader
        self.cellheaderclass=thStyle
        self.cellAttributes = cellAttributes
        if row:
            self.addCells(row)
        
    def addCell(self, cell, celltype=None, cellclass=None, colspan=None, rowspan=None):
        if self.firstColumnHeader and len(self.pieces) == 0:
            celltype="th"
            cellclass=self.cellheaderclass
        elif celltype == None:
            celltype = self.celltype
        
        if celltype == None:
            celltype = "td"
        
        if cellclass==None:
            cellclass=self.cellclass
        
        if(self.cellAttributes):
            attributes = self.cellAttributes
        else:
            attributes = {}
        if colspan:
            attributes['colspan'] = colspan
        if rowspan:
            attributes['rowspan'] = rowspan
        
        if cell == None:
            cell = ""
        
        self.addPiece(part(code=celltype, style=cellclass, content=cell, attributes=attributes))

    def addCells(self, cells):        
        
        for cell in cells:
            self.addCell(cell)

    def columnCount(self):
        return len(self.pieces)


#lists

class linkedList(part):
    def __init__(self, links=None, outer = "ul", inner="li", style=None, iclass=None, aclass=None, id=None, attributes=None):
        part.__init__(self, code=outer, style=style, id=id, attributes=attributes)
        self.innercode = inner
        self.innerstyle = iclass
        self.aclass = aclass
        if isinstance(links, list):
            self.addLinks(links)

    def addLink(self, link):
        [url, name] = link
        
        attributes={"href": url}
        if(self.aclass):
            attributes["class"] = self.aclass
        
        link = part("a", attributes=attributes, content=name)
        listitem = part(self.innercode, content=link, style=self.innerstyle)
        self.pieces.append(listitem)
    
    def addLinks(self, links):
        theLinks = []
        for link in links:
            self.addLink(link)

class simpleList(part):
    def __init__(self, items=None, outer = "ul", inner="li", defaultname=None, default=None, style=None, iclass=None, id=None, attributes=None):
        part.__init__(self, code=outer, style=style, id=id, attributes=attributes)
        self.innercode = inner
        self.innerstyle = iclass
        self.defaultname = defaultname
        self.default=default
        if isinstance(items, list):
            self.addItems(items)
            
    def addItem(self, item):
        attributes = {}
        if self.defaultname:
            if item == self.default:
                attributes[self.defaultname] = None
    
        theItem = part(self.innercode, content=item, style=self.innerstyle, attributes=attributes)
        self.pieces.append(theItem)

    def addItems(self, items):
        theList = []
        for item in items:
            self.addItem(item)

#individual pieces

class image(part):
    def __init__(self, src, alt=None, align=None, style=None, id=None, attributes=None):
        if attributes == None:
            attributes = {}
        attributes['src'] = src
        if alt:
            attributes['alt'] = alt
        if align:
            attributes['align'] = align

        part.__init__(self, 'img', style=style, id=id, attributes=attributes)

class link(snippet):
    def __init__(self, content=None, url=None, posttext=None, pretext=None, style=None, id=None, attributes=None):
        if url != None:
            if attributes == None:
                attributes = {}
            attributes['href'] = url

        snippet.__init__(self, "a", content, posttext, pretext, style, id, attributes)
        

#forms

class form(part):
    def __init__(self, submitText="Submit", pieces=None, method="get", action='./', submitName = None, submitAction=None, headline=None, headlineLevel = 2, style=None, attributes=None):
        self.submitText = submitText
        self.submitName = submitName
        self.making = None
        if attributes == None:
            attributes = {}
        if action != None:
            attributes['action'] = action
        if method != None:
            attributes['method'] = method
        if submitAction != None:
            attributes['onSubmit'] = '"' + submitaction + '"'
        
        part.__init__(self, 'form', style=style, attributes=attributes)
        
        if headline != None:
            headcode = "h" + headlineLevel
            self.addPart(headcode, content=headline)
        
        self.addPieces(pieces)


    def make(self, tab=''):
        if self.making:
            return part.make(self, tab)
        else:
            if self.submitName:
                submitButton = input("submit", value=self.submitText, name=self.submitName)
            else:
                submitButton = input("submit", value=self.submitText)
            trueForm = self
            trueForm.making = 1
            trueForm.addPiece(submitButton)
            pageContent = trueForm.make(tab)
            return pageContent

class input(part):
    def __init__(self, type, name=None, value=None, size=None, maxlength=None, style=None, id=None, attributes=None):
        if attributes == None:
            attributes = {}

        attributes['type'] = type
        if name:
            attributes['name'] = name
        if value!=None:
            attributes['value'] = value
        if size:
            attributes['size'] = size
        if maxlength:
            attributes['maxlength'] = maxlength

        part.__init__(self, 'input', style=style, id=id, attributes=attributes)

class select(simpleList):
    def __init__(self, name, items=None, default=None, style=None, iclass=None, id=None, attributes=None):
        if attributes==None:
            attributes={}
        attributes['name'] = name

        simpleList.__init__(self, items, outer='select', inner='option', defaultname='selected', default=default, style=style, iclass=iclass, id=id, attributes=attributes)
        
class textinput(part):
    def __init__(self, name=None, text=None, value=None, size=None, maxlength=None, style=None, id=None, attributes=None, type="text", tableRow=None):
        if (text == None):
            text = name
        self.field = input(type=type, name=name, value=value, size=size, maxlength=maxlength, style=style, id=id, attributes=attributes)
        self.text = text
        
        if tableRow == None:
            part.__init__(self, 'p', style=style, attributes=attributes)
            self.addPiece(self.text)
            self.addPiece(self.field)
        else:
            part.__init__(self, 'tr', style=style, attributes=attributes)
            self.addPart('th', content=self.text)
            self.addPart('td', content=self.field)



#need some functions for HTML
#ought to be somewhere else in Python?
#cgi.escape only seems to do <, >, and &
from htmlentitydefs import entitydefs
import re

entitydefs_inverted = {}
for k,v in entitydefs.items():
    entitydefs_inverted[v] = k

needencoding = re.compile('|'.join(entitydefs.values()))
alreadyencoded = re.compile('&\w+;|&#[0-9]+;')

#encodes any special characters to their HTML equivalents
def encode(text, skip=None, once_only=1):
    # if extra_careful, check to see if this text has already been converted
    if not (once_only and alreadyencoded.findall(text)):
        if not isinstance(skip, list):
            skip = [skip]

        #do ampersands on their own or we might end up converting our conversions
        if '&' not in skip:
            text = text.replace('&','&amp;')
            skip.append('&')

        needlist= []
        #grab the characters in the text that need encoding
        for x in needencoding.findall(text):
            #and make sure we aren't skipping them
            if x not in skip:
                needlist.append(x)

        for uncoded in needlist:
            encoded = entitydefs_inverted[uncoded]
            #if it is not a numerical encoding, we need to do the & and ; ourselves
            if not encoded.startswith('&#'):
                encoded = '&%s;'%entitydefs_inverted[uncoded]
    
            text = text.replace(uncoded, encoded)

    return text

# a list of comment strings
class ResultComment:
        
    #constructeur
    def __init__(self,comment=""):
        if(not isinstance(comment,basestring)):
            raise "Error : trying to add an object which is not of the 'basestring' type"
        
        if(comment==""):
            self.commentList = []
        else:
            self.commentList = [comment]

    #ajoute un commentaire
    def addComment(self,comment):
        if(not isinstance(comment,basestring)):
            raise "Error : trying to add an object which is not of the 'basestring' type"
        self.commentList.append(comment)
    
    # renvoie l'ensemble des commentaires sous forme de chaine
    def getAllCommentsAsAString(self):
        commentString = ""
        for comment in self.commentList:
            commentString += comment+"\n"
        return commentString
    
    # renvoie la liste de commentaires (liste de strings)
    def getCommentList(self):
        return self.commentList
    
    #la liste de commentaires est-elle vide ?
    def isEmpty(self):
        return (len(self.commentList)==0)
    
    #operateur d'addition
    def __add__(self,testResultComment):
        if(not isinstance(testResultComment,ResultComment)):
           raise "Error : trying to add an object which is not of the 'ResultComment' type"
        
        _testResultComment = self        
        for comment in testResultComment.getCommentList():
            _testResultComment.addComment(comment)
        return _testResultComment

# Result : un booleen, des commentaires (errorResultComments) pour expliquer pourquoi le resultat est False,
# (ajoutes seulement si le resultat est faux) et des commentaires generaux generalResultComments
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
                        
        return Result(_resultBool,_errorResultComments,_generalResultComments)
        
# a Result + a test name and test description
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
    
# a collection of TestResult + a test name and test description
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
    
# a collection of ArTestResult + a name and description
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
        
        #Ajout sommaire qui sera complété plus tard...
        self.pageBody.addPart('h2',content="Résumé des operations effectuées")
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
                           
                           #si le mot lui-même est plus grand que la limite
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
    
    #Considéré comme un ArTestResult avec seulemen un titre + description
    def addTestResult(self,testResult):
        if(not isinstance(testResult,TestResult)):
           raise "Error : trying to add an object which is not of the 'TestResult' type"       
        
        arTestResult = ArTestResult(testResult.getTestName(),testResult.getTestDescription())        
        arTestResult.addTestResult(testResult)
        self.addArTestResult(arTestResult)
    
    #Considéré comme plusieurs TestResults + un titre + description
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
        
        #Création sommaire
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
        
        #Ajout du sommaire à la page
        self.summary.addPiece(summaryPart)           
        
        fullPage.addPiece(self.pageBody)
        htmlCodeString = fullPage.make()        
        outputFile.write(htmlCodeString)

def string_multiSplit(string,sepList):
    stringList = [string]
    
    #split
    for sep in sepList:
        newStringList = []
        for s in stringList:
            splitStringList = s.split(sep)
            newStringList.extend(splitStringList)
        stringList = newStringList
        
    #suppression des chaines vides   
    i = 0
    while(i<len(stringList)):
        if(stringList[i] == ""):
            del stringList[i]
        else:
            i += 1
                
    return stringList   

if __name__ == "__main__":
    outputDirName = os.curdir
    arTestResultsHandler = HTMLArTestResultsHandler()
    fileDateString = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mmin%Ssec")
    outputHTMLFilename = outputDirName+"/log_texturePublisher_"+fileDateString+".html"#"_"+machineName+"_"+userName+".html"        
    initHtmlOutputTestResult = TestResult("Initialisation du log de sortie HTML","Fichier : "+outputHTMLFilename)
    try:
        outputHTMLFile = open(outputHTMLFilename,"w")    
    except:
        initHtmlOutputTestResult += Result(False,ResultComment("Impossible d'ouvrir le fichier en ecriture."))
        arTestResultsHandler.addTestResult(_initHtmlOutputTestResult)
        
    #arTestResultCollection = publishTextureDirectory(inputDirName,outputDirName,outputResolutionString,outputFormat,outputAlphaFormat,outputJPEGQuality,outputRoofJPEGQuality,maxSizePassed,maxSize)
        
    ###########################################
    #Fin de l'execution et ecriture du log de sortie
    #arTestResultsHandler.addArTestResultCollection(arTestResultCollection) 
    arTestResultsHandler.saveAsHTML(outputHTMLFile)
    outputHTMLFile.close()
    os.chmod(outputHTMLFilename,0777)
    
    print "done."
