#!/usr/bin/env python
# -*- coding: iso-8859-1 -*- 

import sys
import string
import re
import getopt
import os
import os.path
import glob
import copy
import shutil
import gdal
import math
import datetime

def printUsage(resultOk):
    print "********************************************************************************"
    print "texturePublisher.py -i <REPERTOIRE TEXTURES> -r <RESOLUTION>"
    print "                    -o <REPERTOIRE SORTIE>"    
    print "                   [-f <FORMAT SORTIE>] [--fa <FORMAT SORTIE ALPHA>]"
    print "                   [-q <QUALITE JPEG>] [--qt <QUALITE JPEG TOITS>]"
    print "                   [-m <TAILLE MAX>]"
    print "********************************************************************************"
    print "Programme permettant de publier une arborescence de textures PNG et JPEG"
    print "a des resolutions differentes"
    print "********************************************************************************"
    print "Description des parametres:"
    print "REPERTOIRE TEXTURES: le repertoire contenant les textures a zoomer."
    print "RESOLUTION: la resolution de zoom en cm. Ex: 12.5, 50..."
    print "REPERTOIRE SORTIE: le repertoire de sortie"
    print "FORMAT SORTIE: JPEG (par defaut) ou PNG"
    print "FORMAT SORTIE ALPHA: PNG (par defaut) ou JPEG"
    print "QUALITE JPEG: compression JPEG entre 0 et 100. 75 par defaut."
    print "QUALITE JPEG TOITS : compression JPEG entre 0 et 100. 75 par defaut."
    print "TAILLE MAX : la taille maximum (doit etre une puissance de 2)."
    print "********************************************************************************"
    print "*Chaque texture a traiter doit etre placee dans un repertoire dont le nom"
    print " indique sa resolution en cm. Ex: 'textures_10cm', '11.5cm', 'toits_12,5cm'..."
    print "*Les textures dont le nom se termine par _a sont traitees comme avec ALPHA"
    print "*Si une sortie JPEG est requise, les textures de toits sont compressees"
    print " avec le taux <QUALITE JPEG TOITS> si leur nom contient le mot 'toit'."
    print "*si une sortie PNG est requise, les textures sans alpha sont forcees en 24 bits." 
    print "********************************************************************************"
    if(resultOk):
        sys.exit(0)
    else:
        sys.exit(1)

############################################################################################
############################################################################################
############################################################################################
############################################################################################
# Fonctions de bases sur les fichiers

# assumes that path exists
def getDirName(path):
    return normalizePath(os.path.dirname(path))

# returns the absolute path of the given path
# assumes that path exists
def getAbsPath(path):
    return normalizePath(os.path.abspath(path))

# returns the basename
def getBasename(path):
    return os.path.basename(path)

# returns the basename without the extension
# ex: '/raid/projects/pouet/bidule.txt' => 'bidule'
# ex: '/raid/projects/pouet/' => ''
# NB : it is not necessary that the path exist
def getBaseNameWithoutExtension(path):
    return os.path.splitext(os.path.basename(path))[0]

# normalizes the path
# modify paths so that /rep1/rep11/../rep12 => /rep1/rep12 (on unix)
# NB : on windows, the path separator is \\, on unix it is /
def normalizePath(path):
    unixPath = copy.deepcopy(os.path.normpath(path))
    return os.path.normpath(unixPath.replace('\\','/'))


# True if the absolute fileName path exists (no wildcards allowed)
def fileExists(fileName):
    return os.path.isfile(fileName)

# returns the list of normalized fileNames (see above for "normalizePath") corresponding to the given path
# ([] if the path does not exist, or if nothing was found)
# NB : does not search into sub-directories
# NB : wildcards are allowed
# ex for unix : '/raid/projects/pouet/' => '/raid/projects/pouet/'
# ex for unix : '/raid/projects/pouet/*' => a list of all files and directories in directory "pouet"
# ex for unix : '/raid/projects/pouet/*.txt' => a list of all TXT files in directory "pouet"
# etc...
def getFileListFromPath(path):
    fileList = glob.glob(normalizePath(path))
    normalizedFileList = []
    for fileName in fileList:
        normalizedFileList.append(normalizePath(fileName))
    return normalizedFileList

# Given a file in directory baseDir, checks if the filename "relativeOrAbsoluteFileName" exists
# as an absolute filename or as a relative filename from this directory baseDir
# return a boolean
def fileExistsAsAbsoluteOrRelative(baseDir,relativeOrAbsoluteFileName):
    return (fileExists(relativeOrAbsoluteFileName) or fileExists(baseDir+"/"+relativeOrAbsoluteFileName))

#checks if path exists (Wildcards allowed)
def pathExists(pathName):
    if(pathName==""):
        return False #car os.path.normPath renvoie "." quand on lui passe ""
    else:
        normPath = os.path.normpath(pathName)
        return (os.path.exists(normPath) or (len(glob.glob(normPath))>0))
    
# checks that absolute and relative (to directory "basedir" ) fileNames in fileNamesList exist
# return a boolean + a list of comments for each file that was not found
# NB : no wild cards allowed
def fileExistInBaseDirList(baseDirList,fileBaseName):
    if(len(baseDirList)==0):
        return Result(False,ResultComment("La liste des repertoires est vide."))
    if(len(fileBaseName)==0):
        return Result(False,ResultComment("Le nom de fichier est vide."))
    
    i = 0
    exists = False
    while( (i<len(baseDirList)) and (not exists) ):    
        baseDir = baseDirList[i]
        exists = fileExists(baseDir+"/"+fileBaseName)
        i += 1

    if(exists):
        return Result(True,ResultComment(""),ResultComment(""))
        #return Result(True,ResultComment(""),ResultComment("Le fichier '"+fileBaseName+"' a ete trouve dans le repertoire '"+str(baseDir)+"'."))
    else:
        return Result(False,ResultComment("Le fichier '"+fileBaseName+"' n'a pas ete trouve a partir des repertoires '"+str(baseDirList)+"'."))

#copy a file (relative or absolute path) to a destination path (output dir, or new filename)
def copyFile(srcFilename,destPath):   
    try:
        shutil.copy(srcFilename,destPath)
    #Interruption clavier (CRTR+C...)
    except(KeyboardInterrupt):
        print ""
        print "> ERREUR: Interruption du programme par l'utilisateur !"
        print "> Provoque sortie du programme."
        sys.exit(1)        
    except:
        return False
    
    basename = getBasename(srcFilename)
    absDestPath = getAbsPath(destPath)    
    return (fileExistsAsAbsoluteOrRelative(absDestPath,basename) or pathExists(absDestPath))

#return a boolean indicating if the directories could be made
def mkdir(path):     
    if(not pathExists(path)):
        try:
            os.makedirs(path)
        #Interruption clavier (CRTR+C...)
        except(KeyboardInterrupt):
            print ""
            print "> ERREUR: Interruption du programme par l'utilisateur !"
            print "> Provoque sortie du programme."
            sys.exit(1)        
        except:
            return False
        return pathExists(path)
    else:
        return True

def hasExtension(filename,extensionList):
    filenameExtension = InsensitiveString(os.path.splitext(filename)[1])
    for extension in extensionList:
        if(filenameExtension==InsensitiveString(extension)):
            return True
    return False

def basenameHasSuffix(filename,suffixList):
    basename = InsensitiveString(os.path.splitext(filename)[0])
    for suffix in suffixList:
        if(basename.endswith(suffix)):
            return True
    return False

def getSubDirectories(dirName):
    thingsInDir = os.listdir(dirName)
    subdirList = []
    for thing in thingsInDir:
        if(os.path.isdir(dirName)):
            subdirList.append(thing)
    return subdirList


#removes given filenames (wildcards allowed) and directories
#only removes the last directory in directory path
def cleanPath(path):
    fileList = getFileListFromPath(path)
    cleanResult = True
    for fileName in fileList:
        try:
            os.remove(fileName)
        except:
            #si c'est un repertoire
            if(os.path.isdir(fileName)):
                try:
                    os.rmdir(fileName)
                except:
                    cleanResult = False
            else:
                if(os.path.exists(fileName)):
                    cleanResult = False
                else:
                    cleanResult = True #pas grave si on arrive pas a supprimer ce fileName car il n'existe pas
            
    return cleanResult

############################################################################################
############################################################################################
############################################################################################
############################################################################################
#Fonctions de base sur les chaines

def isInt( str ):
    ok = True
    try:
        ok = (int(str)==float(str))       
    except ValueError:
        ok = False
    return ok

def isFloat( str ):
    ok = True
    try:
        float(str)        
    except ValueError:
        ok = False
    return ok

class InsensitiveString(str):
    """Case insensitive strings class.
    Performs like str except comparisons are case insensitive."""

    def __init__(self, strMe):
        str.__init__(self, strMe)
        self.__lowerCaseMe = strMe.lower()

    def __repr__(self):
        return "iStr(%s)" % str.__repr__(self)

    def __eq__(self, other):
        return self.__lowerCaseMe == other.lower()

    def __lt__(self, other):
        return self.__lowerCaseMe < other.lower()

    def __le__(self, other):
        return self.__lowerCaseMe <= other.lower()

    def __gt__(self, other):
        return self.__lowerCaseMe > other.lower()

    def __ne__(self, other):
        return self.__lowerCaseMe != other.lower()

    def __ge__(self, other):
        return self.__lowerCaseMe >= other.lower()

    def __cmp__(self, other):
        return cmp(self.__lowerCaseMe, other.lower())

    def __hash__(self):
        return hash(self.__lowerCaseMe)

    def __contains__(self, other):
        return other.lower() in self.__lowerCaseMe

    def count(self, other, *args):
        return str.count(self.__lowerCaseMe, other.lower(), *args)

    def endswith(self, other, *args):
        return str.endswith(self.__lowerCaseMe, other.lower(), *args)

    def find(self, other, *args):
        return str.find(self.__lowerCaseMe, other.lower(), *args)
    
    def index(self, other, *args):
        return str.index(self.__lowerCaseMe, other.lower(), *args)

    def lower(self):   # Courtesy Duncan Booth
        return self.__lowerCaseMe

    def rfind(self, other, *args):
        return str.rfind(self.__lowerCaseMe, other.lower(), *args)

    def rindex(self, other, *args):
        return str.rindex(self.__lowerCaseMe, other.lower(), *args)

    def startswith(self, other, *args):
        return str.startswith(self.__lowerCaseMe, other.lower(), *args)
    
    def replace(self,old,new):
        index = self.find(old)
        
        length = len(old)
        
        newStr = ""
        lastIndex = 0
        while(index!=-1):
            #print newStr
            #print index
            #print self[lastIndex:index]
            newStr += self[lastIndex:index]
            newStr += new
            lastIndex = index+length
            #print lastIndex
            index = self.find(old,lastIndex)
                
        newStr += self[lastIndex:len(self)]

        return newStr


#splits a string with a list of separators
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

def getDuplicateStrings(stringList):    
    alreadyCheckedStringList = []
    duplicateStringList = []
    for string in stringList:
        if(string in alreadyCheckedStringList):
            duplicateStringList.append(string)
        else:
            alreadyCheckedStringList.append(string)
    return duplicateStringList

############################################################################################
############################################################################################
############################################################################################
############################################################################################
# Fonction de log au format HTML

#!/usr/bin/env python
# -*- coding: iso-8859-1 -*- 

#makeHTML.py version 0.8 May 1, 2005 Jerry Stratton
#
#part(code="tag" (defaults to paragraph), content="text" style="css style name", id="css id", attributes={named array of attributes for tag}
#    addAttribute(attributename="name for tag attribute", attributevalue="value for tag attribute")
#    addPart(code, content, style, id, attributes): adds at end
#    addPiece(thePart=another part object or "content text")
#    addPieces(pices=a list of part objects or content texts)
#    insertPart(code, content, style, id, attributes): inserts at start
#    insertPiece(thePart)
#    make(tab="initial tabs")
#    makePart(code, content, style, id, attributes): returns a part object
#    __len__: parts support the len() function; return number of pieces directly contained
#snippet(code (defaults to "em"), content, posttext="text that comes directly after tag", pretext="text that comes directly before tag", style, id, attributes)
#
#head(title="text for title of page")
#body(title="text for main headline", style, id, attributes)
#page(pieces, style, id, attributes)
#styleSheet(sheet="url of stylesheet", media="relevance of style sheet")
#
#headline(content="text content" (required), level="numerical level", style, id, attributes)
#
#table(rows=list of data for rows, style, thStyle="css style for table headers", tdStyle="css style for table cells",
#        trStyle="css style for table rows", tdBlankStyle="css style for blank cells", firstRowHeader=1--if first row is a header row,
#        firstColumnHeader=1--if first column is a header column, id, attributes)
#    addRow(rowList=[list of cells or data], celltype="th or td", cellclass="css style of cells", attributes, style)
#    addRows(rows=[list of list of cells or data], celltype, cellclass, attributes)
#    columnCount()
#tableByColumn(columns=[list of columns], style, thStyle, tdStyle, trStyle, tdBlankStyle, firstRowHeader, firstColumnHeader, id, attributes)
#    addColumn(columnList=[list of column data or cells], celltype, cellclass, attributes)
#    addColumns(columns=[list of list of columns or column data], celltype, cellclass, attributes)    
#tableColumn(column=[list of data or cells for column], celltype, cellclass, firstRowHeader, thStyle, tdBlankStyle, attributes)
#    addCell(cell="cell or cell content", celltype, cellclass, id, attributes)
#    addCells(column="list of cells or cell contents", celltype, cellclass, attributes)
#tableRow(celltype, row=[list of cells or cell data], style, cellclass, firstColumnHeader, thStyle, id, attributes)
#    addCell(cell="cell or cell content", celltype, cellclass, colspan="numerical span of cell vertically", rowspan="numerical span of cell horizontally")
#    addCells(cells=[list of cells or cell content])
#    columnCount()
#
#linkedList(links=[list of items of the form [url, name]], outer="outer html tag", inner="inner html tag", style="outer css style",
#        iclass="inner css style", id, attributes)
#    addLink(link=[url, name])
#    addLinks(links)
#simpleList(items=[list of text items], outer, inner, defaultname="text for marking default entry", default="text of default entry",
#        style, iclass, id, attributes)
#    addItem(item="text of item")
#    addItems(items)
#
#image(src="url of image", alt="alternate text for image", align="alignment", style, id, attributes)
#link(content, url, posttext, pretext, style, id, attributes)
#
#form(submitText="text of submit button", pieces, method="submit method", action="form action", submitName="name for submit button", submitAction="javascript for submission"
#        headline="headline text", headlineLevel (defaults to 2), style, attributes, id)
#input(type="type of form input", name="name for input", value="default value for input", size="size for input", maxlength="maximum characters accepted",
#        style, id, attributes)
#select(name, items, default, style, iclass, id, attributes
#textinput(name, text, value, size, maxlength, style, id, attributes, type, tableRow=true if this should be a tr row, otherwise it is a paragraph)

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


############################################################################################
############################################################################################
############################################################################################
############################################################################################
#Fonctions en rapport avec l'OS

#Classe pour execution de fonctions avec timeout
def timeout(func, args=(), kwargs={}, timeout_duration=3600, default=False):
    import threading
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except:
                self.result = default             

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.isAlive():
        return default
    else:
        return it.result        

#Execution d'une commande par l'OS
#Retourne un booleen
def execute(command):
    if(len(command)==0):
        return False
    result = os.system(command)
    return (result==0)

        
#Renvoie un TestResult concernant l'execution de la commande passee en parametre
#ATTENTION, les commandes ne peuvent etre arretees, meme si la fonction peut se terminer grace au timeout
#Il est donc necessaire de tuer manuellement tous les processes encore en activite
def execCommand(command="",logFileName="",timeout_duration=1200,searchProgram=True):
    execTestResult = TestResult("Execution","Essaie d'executer la commande '"+command+"'")
    
    execTestResult += Result(isinstance(command,basestring),ResultComment("Execution impossible : la commande a executer n'est pas une chaine de caractere."),ResultComment(""))        
    execTestResult += Result(isinstance(timeout_duration,int) and (not isinstance(timeout_duration,bool)),ResultComment("Execution impossible : la valeur de timeout en parametre n'est pas un entier."),ResultComment(""))        
    execTestResult += Result(isinstance(searchProgram,bool),ResultComment("Execution impossible : la variable 'searchProgram' en parametre n'est pas un booleen."),ResultComment(""))        

    if(execTestResult.getResultBool()):        
    
        if(searchProgram):
            #Recherche du programme (1er element de la commande)
            commandSplitList = string_multiSplit(command,[" "])
            if(len(commandSplitList)<1):
                execTestResult += Result(False,ResultComment("Execution impossible. La commande est vide."),ResultComment(""))        
            else:
                softwareName = commandSplitList[0]
            execTestResult += findExecutable(softwareName)
        
        if(execTestResult.getResultBool()):
        
        #    #Execution "old school" sans timeout
        #    execResult = execute(command)
        #    execTestResult += Result(execResult,ResultComment("Execution impossible. Valeur de retour non nulle."),ResultComment("ATTENTION : Le test de la valeur de retour n'est pas encore code (pb d'uniformite entre programmes)..."))            
            
            #Execution avec "time out"
            defaultTimeOutValue = "timeout"

            #si besoin de logger sortie
            if(logFileName):
                loggingCommand = " >> "+logFileName+" 2>&1 ;"                
                executionDirectory = os.getcwd()                     
                
                #Ajout d'un commentaire de debut d'execution
                executionBeginDateString = datetime.datetime.now().strftime("(%a) %d/%m/%Y %Hh%Mmin %Ssec")
                beginCommand = "python -c 'print \"*******************************************\";print \"************  EXECUTION START  ************\";print \"* Execution Directory : "+executionDirectory+"\";print \"* Commande : "+command+"\";print \"* Date : "+executionBeginDateString+"\";print \"*******************************************\";'"                
                timeout(func=execute,kwargs={"command":beginCommand+loggingCommand},timeout_duration=timeout_duration,default=defaultTimeOutValue)                                
                
                #Execution
                execResult = timeout(func=execute,kwargs={"command":command+loggingCommand},timeout_duration=timeout_duration,default=defaultTimeOutValue)                                

                #Ajout d'un commentaire de fin d'execution
                executionEndDateString = datetime.datetime.now().strftime("(%a) %d/%m/%Y %Hh%Mmin %Ssec")
                endCommand = "python -c 'print \"*******************************************\";print \"*************  EXECUTION END  *************\";print \"* Date : "+executionEndDateString+"\";print \"*******************************************\";'"                
                timeout(func=execute,kwargs={"command":endCommand+loggingCommand},timeout_duration=timeout_duration,default=defaultTimeOutValue)

            else:
                execResult = timeout(func=execute,kwargs={"command":command},timeout_duration=timeout_duration,default=defaultTimeOutValue)

            #Si arret a cause d'un timeout
            if(execResult==defaultTimeOutValue):
                execTestResult += Result(False,ResultComment("Execution impossible, a cause d'un time out (>"+str(timeout_duration)+"seconds). ATTENTION, le programme tourne peut-etre encore !!!"),ResultComment(""))
            else:                
                execTestResult += Result(execResult,ResultComment("Execution apparemment impossible. Valeur de retour non nulle."),ResultComment(""))
    
    return execTestResult    


#returns a Result indicating if the executable was found in one of the directories, and if so, the directory
def findExecutable(executableName):
    findExecutableTestResult = TestResult("Recherche de l'executable '"+executableName+"' dans le SYSTEM PATH","")
    systemPath = os.getenv("PATH")
    findExecutableTestResult += Result((systemPath is not None),ResultComment("Impossible de recuperer le SYSTEM PATH"),ResultComment(""))
    
    if(findExecutableTestResult.getResultBool()==False):
        return findExecutableTestResult
    
    splitStringList = string_multiSplit(systemPath,[";"]) #WINDOWS
    baseDirList = []
    if(len(splitStringList)==0):
        findExecutableTestResult += Result(False,ResultComment("SYSTEM PATH is not valid"),ResultComment(""))
        return findExecutableTestResult
    #seulement WINDOWS possible
    elif(len(splitStringList)>1):
        baseDirList = splitStringList        
    else:
        splitStringList = string_multiSplit(systemPath,[":"]) #LINUX
        
        if(len(splitStringList)==0):
            findExecutableTestResult += Result(False,ResultComment("SYSTEM PATH is not valid"),ResultComment(""))
            return findExecutableTestResult        
        #LINUX OU WINDOWS (avec un seul repertoire dans le PATH)
        elif(len(splitStringList)>=1):
            baseDirList = splitStringList
    
    findExecutableTestResult += fileExistInBaseDirList(baseDirList,executableName)
    return findExecutableTestResult

############################################################################################
############################################################################################
############################################################################################
############################################################################################
#Fonctions de zoom

#Convertit une texture au format JPEG
def convertToJPEG(inputFileName,outputFileName,outputJPEGQuality):
    cmd = "gdal_translate -of JPEG -b 1 -b 2 -b 3 -co 'QUALITY="+str(outputJPEGQuality)+"' "+inputFileName+" "+outputFileName+" > /dev/null 2>&1"       
    return execCommand(cmd)

#Convertit une texture au format PNG 24 bits
def convertTo24BitsPNG(inputFileName,outputFileName):
    cmd = "gdal_translate -of PNG -b 1 -b 2 -b 3 "+inputFileName+" "+outputFileName+" > /dev/null 2>&1"       
    return execCommand(cmd)

#Zoome une texture avec un facteur de zoom
#Sortie: PNG
def resizeTextureWithFactor(inputFileName,outputFileName,resizeFactor):
    cmd = "gdal_zoomPVM -of PNG -f "+str(resizeFactor)+" "+str(resizeFactor)+" -m quality -in "+inputFileName+" -out "+outputFileName+" > /dev/null 2>&1"        
    return execCommand(cmd)

#Zoome une texture dans une nouvelle taille (xsize,ysize)
#Sortie: PNG
def resizeTextureWithSizes(inputFileName,outputFileName,xsize,ysize):
    cmd = "gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName+" > /dev/null 2>&1"        
    return execCommand(cmd)

#Zoome une texture en puissances de 2 superieures
#Sortie: PNG
def resizeTexturePowerOfTwo(inputFileName,outputFileName,limitSize=False,maxSize=1024):
    gdal.AllRegister()
    gdalDataSet = gdal.Open(inputFileName)
    if gdalDataSet is None:
        tr = TestResult("Redimensionnement de l'image '"+inputFileName+"'","")
        tr += Result(False,ResultComment("ERREUR: impossible d'ouvrir l'image"))
        return tr        
    xsize = gdalDataSet.RasterXSize
    ysize = gdalDataSet.RasterYSize
    del gdalDataSet    
    newXSize = math.pow(2,math.ceil(math.log(xsize)/math.log(2)))    
    newYSize = math.pow(2,math.ceil(math.log(ysize)/math.log(2)))
    
    if(limitSize):
        newXSize2 = min(maxSize,newXSize)
        newYSize2 = min(maxSize,newYSize)
    else:
        newXSize2 = newXSize
        newYSize2 = newYSize
        
    tr = resizeTextureWithSizes(inputFileName,outputFileName,newXSize2,newYSize2)
    if( (newXSize2!=newXSize) or (newYSize2!=newYSize) ):
        tr += Result(True,ResultComment(""),ResultComment("Warning: la texture '"+inputFileName+"' a ete resize de "+str(xsize)+"x"+str(ysize)+" vers "+str(newXSize2)+"x"+str(newYSize2)+" au lieu de "+str(newXSize)+"x"+str(newYSize)+"."))
    
    return tr

#Zoome une texture avec un facteur de zoom
#Fait attention a ce que la taille minimale en sortie soit 1x1
#Sortie: PNG
def resizeTexture(inputFileName,outputFileName,resizeFactor):
    gdal.AllRegister()
    gdalDataSet = gdal.Open(inputFileName)
    if gdalDataSet is None:
        tr = TestResult("Redimensionnement de l'image '"+inputFileName+"'","")
        tr += Result(False,ResultComment("ERREUR: impossible d'ouvrir l'image"))
        return tr    
    xsize = gdalDataSet.RasterXSize
    ysize = gdalDataSet.RasterYSize
    del gdalDataSet    
    newXSize = max(1,math.floor(xsize*resizeFactor+0.5))
    newYSize = max(1,math.floor(ysize*resizeFactor+0.5))
    return resizeTextureWithSizes(inputFileName,outputFileName,newXSize,newYSize)


############################################################################################
############################################################################################
############################################################################################
############################################################################################

#gere des noms de repertoires commencant par la resolution, puis suivis de n'importe quelle chaine
def old_getResolutionForDirBaseName(dirBaseName):   
    dirBaseName = dirBaseName.lower()
    decomposedStringList = string_multiSplit(dirBaseName,["cm"," ","_","-"])
    resolutionString = decomposedStringList[0]
    resolutionString = resolutionString.replace(",",".")
    if(not isFloat(resolutionString)):
        return False,None
    else:
        resolution = float(resolutionString)
        return True,resolution

#Gere des noms de repertoires assez elabores...    
def getResolutionForDirBaseName(dirBaseName):       
    dirBaseName = dirBaseName.lower()
    dirBaseName = dirBaseName.replace(" ","")
    dirBaseName = dirBaseName.replace("_","")
    dirBaseName = dirBaseName.replace("","")
    dirBaseName = dirBaseName.replace(",",".")
    import re
    expression = re.compile("([a-z]*)(?P<res>[0-9]+\.?[0-9]*)(cm)([a-z]*)",re.I)
    m = expression.match(dirBaseName)
    if(m is None):
        return False, None        
    dico = m.groupdict()
    if(not dico.has_key("res")):
        return False, None
    else:
       resolution = float(dico["res"])
       return True,resolution

#Verifie la coherence du repertoire d'entree et retourne la liste des textures avec leur resolution
#En sortie : un ArTestResult, un dico contenant pour chaque resolution la liste des textures trouvees
def checkAndDecodeDirectory(dirName):
   
    arTestResult = ArTestResult("Decodage du repertoire d'entree","Verification de la coherence du repertoire d'entree et listage des textures selon leur resolution")

    #Verification de l'existence du repertoire d'entree
    testResult = TestResult("Verification de l'existence du repertoire d'entree","")
    testResult += Result(pathExists(dirName),ResultComment("ERREUR: le repertoire '"+dirName+"' n'existe pas."))
    arTestResult.addTestResult(testResult)
    if(not arTestResult.getResultBool()):
        return arTestResult,{}
           
    #On verifie le formatage du nom des sous-repertoires
    testResult = TestResult("Verification du formatage du nom des sous-repertoires","")
    subdirList = getSubDirectories(dirName)    
    dirResDict = {}
    for subdir in subdirList:        
        result, res = getResolutionForDirBaseName(subdir)
        if(not result):
            testResult += Result(True,ResultComment(""),ResultComment("Warning: la resolution du repertoire '"+subdir+"' n'a pu etre trouvee")) 
        else:
            testResult += Result(True,ResultComment(""),ResultComment("La resolution trouvee pour le repertoire '"+subdir+"' est "+str(res)))
            if(res<=0):
                testResult += Result(False,ResultComment("ERREUR: la resolution du repertoire '"+subdir+"' est <0 !"))
            else:
                dirResDict[subdir] = res
    
    arTestResult.addTestResult(testResult)
    if(not arTestResult.getResultBool()):
        return arTestResult,{}
    
    #Pour chaque resolution, on liste les textures    
    testResult = TestResult("Listage des textures a zoomer","")
    resTexturesDict = {}    
    for subdir in dirResDict.keys():
        res = dirResDict[subdir]        
        imageFileNameList = []
        fileNameList = getFileListFromPath(inputDirName+"/"+subdir+"/*")
        for fileName in fileNameList:
            if(hasExtension(fileName,[".jpeg",".jpg",".png"])):
                imageFileNameList.append(fileName)
        
        if(not resTexturesDict.has_key(res)):
            resTexturesDict[res] = imageFileNameList
        else:
            resTexturesDict[res].extend(imageFileNameList)    
    testResult += Result(True,ResultComment(""),ResultComment("Liste des textures trouvees par resolution: "+str(resTexturesDict)))
    arTestResult.addTestResult(testResult)
    if(not arTestResult.getResultBool()):
        return arTestResult,{}
            
    #On verifie qu'il n'y a pas de "doublons"
    #cad que plusieurs textures ont le meme radical
    testResult = TestResult("Verification des doublons","")
    texList = []
    for res in resTexturesDict.keys():    
        texList.extend(resTexturesDict[res])
        
    texBaseNameWithoutExtList=[]
    for texFileName in texList:
        texBaseNameWithoutExtList.append(getBaseNameWithoutExtension(texFileName))
    
    duplicateTexBaseNameWithoutExtList = getDuplicateStrings(texBaseNameWithoutExtList)
    if(len(duplicateTexBaseNameWithoutExtList)>0):
        testResult += Result(True,ResultComment(""),ResultComment("WARNING: des textures portent le meme nom : "+str(duplicateTexBaseNameWithoutExtList)))
    arTestResult.addTestResult(testResult)
    
    return arTestResult,resTexturesDict

############################################################################################
############################################################################################
############################################################################################
############################################################################################

#Fonction executant le zoom des textures
#Nécessite un dico contenant pour chaque resolution, la liste des chemins des textures trouvees
#* Cree les repertoires temporaires de sortie
#* Realise les zooms
#Retourne un ArTestResult
def publishTextures(resTexturesDict,outputResolutionString,outputFormat,outputAlphaFormat,outputJPEGQuality,outputRoofJPEGQuality,outputDirName,limitSize=False,maxSize=1024):
    
    arTestResult = ArTestResult("Zoom des textures","")
    
    #Verification de l'existence du repertoire de sortie
    testResult = TestResult("Verification de l'existence du repertoire de sortie","")
    testResult += Result(pathExists(outputDirName),ResultComment("ERREUR: le repertoire '"+outputDirName+"' n'existe pas."))
    arTestResult.addTestResult(testResult)
    if(not arTestResult.getResultBool()):
        return arTestResult    
    
    #Creation repertoires de sortie
    testResult = TestResult("Creation des repertoires de sortie","")
    firstZoomDir = outputDirName+"/textures_"+str(outputResolutionString)+"cm/"
    secondZoomDir = outputDirName+"/textures_"+str(outputResolutionString)+"cm_puiss2/" 
    testResult += Result(mkdir(firstZoomDir),ResultComment("ERREUR: impossible de creer le repertoire de sortie '"+firstZoomDir+"'"))
    testResult += Result(mkdir(secondZoomDir),ResultComment("ERREUR: impossible de creer le repertoire de sortie '"+secondZoomDir+"'"))
    arTestResult.addTestResult(testResult)
    if(not arTestResult.getResultBool()):
        return arTestResult    
    
    #Zoom des textures
    #(dans le sens des resolutions decroissantes pour tjrs traiter
    #en dernier les textures les plus resolues en cas de doublons)
    testResult = TestResult("Zoom de chaque texture","")
    outputResolution = float(outputResolutionString)    
    resolutionsList = resTexturesDict.keys()
    resolutionsList.sort(reverse=True)
    for res in resolutionsList:
        resizeFactor = res/outputResolution        
        
        textureFileNameList = resTexturesDict[res]        
        for textureFileName in textureFileNameList:                    
            basenameWithoutExt = getBaseNameWithoutExtension(textureFileName)
                        
            #1er zoom (a resolution voulue)            
            firstOutputFileName = normalizePath(firstZoomDir+"/"+basenameWithoutExt+".png")
            firstZoomTestResult = resizeTexture(textureFileName,firstOutputFileName,resizeFactor)
            if(not firstZoomTestResult.getResultBool()):
                testResult += Result(False,ResultComment("ERREUR: impossible de redimensionner la texture '"+textureFileName+"' en '"+firstOutputFileName+"'")+firstZoomTestResult.getErrorResultComment(),firstZoomTestResult.getGeneralResultComments())
            else:
                testResult += Result(True,ResultComment(""),firstZoomTestResult.getGeneralResultComments())
                #Zoom en puissances de 2
                secondOutputFileName = normalizePath(secondZoomDir+"/"+basenameWithoutExt+".png")
                secondZoomTestResult = resizeTexturePowerOfTwo(firstOutputFileName,secondOutputFileName,limitSize,maxSize)
                if(not secondZoomTestResult.getResultBool()):
                    testResult += Result(False,ResultComment("ERREUR: impossible de redimensionner la texture '"+firstOutputFileName+"' en '"+secondOutputFileName+"'")+secondZoomTestResult.getErrorResultComment(),secondZoomTestResult.getGeneralResultComments())
                else:
                    testResult += Result(True,ResultComment(""),secondZoomTestResult.getGeneralResultComments())
                    #Conversion en JPEG si necessaire ou copie
                    hasAlpha = basenameHasSuffix(basenameWithoutExt,["_a","_alpha"])                    
                    format = ""
                    if(hasAlpha):
                        format = outputAlphaFormat
                    else:
                        format = outputFormat
                    
                    #Si format de sortie PNG
                    if(format == "PNG"):
                        #Copie
                        convertTo24BitsPNG(secondOutputFileName,outputDirName)
                        #Si alpha, on conserve en PNG 32 bits
                        if(hasAlpha):
                            copyResult = copyFile(secondOutputFileName,outputDirName)
                            if(not copyResult):
                                testResult += Result(False,ResultComment("ERREUR: impossible de copier la texture '"+secondOutputFileName+"' vers le repertoire '"+outputDirName+"'"))
                        #si pas d'alpha, on passe en PNG 24 bits
                        else:
                            lastOutputFileName = normalizePath(outputDirName+"/"+basenameWithoutExt+".png")
                            conversionResult = convertTo24BitsPNG(secondOutputFileName,lastOutputFileName)
                            if(not conversionResult.getResultBool()):
                                testResult += Result(False,ResultComment("ERREUR: impossible de convertir la texture '"+secondOutputFileName+"' en PNG 24 bits '"+lastOutputFileName+"'"))                            
                    else:
                        #Conversion en JPEG
                        lastOutputFileName = normalizePath(outputDirName+"/"+basenameWithoutExt+".jpg")                        
                        jpegCompressionRate = outputJPEGQuality #par defaut
                        #si "toit"
                        if(InsensitiveString(basenameWithoutExt).__contains__("toit")):
                            testResult += Result(True,ResultComment(""),ResultComment("Le fichier '"+getBasename(secondOutputFileName)+"' contient le mot 'toit' dans son nom et va etre traite en consequence."))
                            jpegCompressionRate = outputRoofJPEGQuality
                            
                        conversionResult = convertToJPEG(secondOutputFileName,lastOutputFileName,jpegCompressionRate)
                        if(not conversionResult.getResultBool()):
                            testResult += Result(False,ResultComment("ERREUR: impossible de convertir la texture '"+secondOutputFileName+"' en '"+lastOutputFileName+"'"))

    arTestResult.addTestResult(testResult)
    
    #Suppression des repertoires temporaires
    cleanTestResult = TestResult("Suppression des repertoires temporaires","")
    cleanBoolResult1 = cleanPath(firstZoomDir+"/*.png") and cleanPath(firstZoomDir)
    cleanBoolResult2 = cleanPath(secondZoomDir+"/*.png") and cleanPath(secondZoomDir)
    cleanTestResult += Result(cleanBoolResult1,ResultComment("ERREUR: impossible de supprimer le repertoire temporaire '"+firstZoomDir+"'"))
    cleanTestResult += Result(cleanBoolResult2,ResultComment("ERREUR: impossible de supprimer le repertoire temporaire '"+secondZoomDir+"'"))
    arTestResult.addTestResult(cleanTestResult)
    
    return arTestResult
            
            
############################################################################################
############################################################################################
############################################################################################
############################################################################################
                    
#Fonction principale
#Decode le repertoire d'entree
#et, si ok, demander le zoom des textures trouvees (fonction publishTextures)
#Retourne un booleen
def publishTextureDirectory(inputDirName,outputDirName,outputResolutionString,outputFormat,outputAlphaFormat,outputJPEGQuality,outputRoofJPEGQuality,limitSize=False,maxSize=1024):
    arTestResultCollection = ArTestResultCollection("Texture Publisher")
    
    #Affichage infos generales sur l'execution
    executionDirectory = os.getcwd()
    infosGenerales =  "******************************************************"+"\n"
    infosGenerales += "Repertoire d'execution   : "+executionDirectory+"\n"
    infosGenerales += "Repertoire d'entree      : "+inputDirName+"\n"
    infosGenerales += "Repertoire de sortie     : "+outputDirName+"\n"
    infosGenerales += "Resolution               : "+outputResolutionString+"\n"
    infosGenerales += "Format de sortie         : "+outputFormat+"\n"
    infosGenerales += "Format de sortie (alpha) : "+outputAlphaFormat+"\n"
    infosGenerales += "Qualite (JPEG)           : "+str(outputJPEGQuality)+"\n"
    infosGenerales += "Qualite (toits JPEG)     : "+str(outputRoofJPEGQuality)+"\n"    
    if(limitSize):
        infosGenerales += "Taille max               : "+str(maxSize)+"\n"
    infosGenerales += "******************************************************"
    arTestResult0 = ArTestResult("Infos generales sur l'execution",infosGenerales)
    print infosGenerales
    arTestResultCollection.addArTestResult(arTestResult0)
    
    #Decodage du repertoire d'entree    
    arTestResult1,resTexturesDict = checkAndDecodeDirectory(inputDirName)    
    arTestResultCollection.addArTestResult(arTestResult1)
    print "******************************************************"
    if(not arTestResult1.getResultBool()):
        return arTestResultCollection    
    
    #Zoom des textures trouvees...    
    arTestResult2 = publishTextures(resTexturesDict,outputResolutionString,outputFormat,outputAlphaFormat,outputJPEGQuality,outputRoofJPEGQuality,outputDirName,limitSize,maxSize)    
    arTestResultCollection.addArTestResult(arTestResult2)    
    print "******************************************************"
    return arTestResultCollection

############################################################################################
############################################################################################
############################################################################################
############################################################################################    
# MAIN

if __name__ == '__main__':

    try:
       # parse command line options
        try:
            opts, args = getopt.getopt(sys.argv[1:],"hi:o:r:f:a:q:t:m:", ["help","input==","output==","resolution==","format==","fa==","quality==","qt==","maxsize=="])
        except getopt.error, msg:
            print msg
            print "HELP : -h"
            printUsage(True)
        
        if( (len(args)==0) and (len(opts)==0) ):
            printUsage(True)
    
        # process options
        inputPassed = False
        inputDirName = ""
        outputPassed = False
        outputDirName = ""
        outputResPassed = False
        outputResolutionString = None
        availableOutputFormats = ["JPEG","PNG"]
        outputFormatPassed = False
        outputFormat = "JPEG"
        outputAlphaFormatPassed = False
        outputAlphaFormat = "PNG"
        outputJPEGQualityPassed = False
        outputJPEGQuality = 75
        outputRoofJPEGQualityPassed = False
        outputRoofJPEGQuality = 75
        maxSizePassed = False
        maxSize = None         
        
        for opt, arg in opts:
            if opt == "-h":
                printUsage(True)
            if opt in ("-i"):
                inputPassed = True
                inputDirName = arg
            if opt in ("-o"):
                outputPassed = True
                outputDirName = arg                   
            if opt in ("-r"):
                outputResPassed = True
                outputResolutionString = arg                   
            if opt in ("-f"):
                outputFormatPassed = True
                outputFormat = arg
            if opt in ("--fa="):
                outputAlphaFormatPassed = True
                outputAlphaFormat = arg
            if opt in ("-q"):
                outputJPEGQualityPassed = True
                outputJPEGQuality = arg
            if opt in ("--qt="):
                outputRoofJPEGQualityPassed = True
                outputRoofJPEGQuality = arg
            if opt in ("-m"):
                maxSizePassed = True
                maxSize = arg                                                       
        cmdLineErrorFound = False
             
        if(not inputPassed):
            print "ERREUR: pas de repertoire d'entree specifie"
            cmdLineErrorFound = True
        if(not outputPassed):
            print "ERREUR: pas de repertoire de sortie specifie."
            cmdLineErrorFound = True
        
        if(outputResPassed):
            if(not isFloat(outputResolutionString)):
                print "ERREUR: la resolution doit etre un nombre flottant."
                cmdLineErrorFound = True
        
        if(outputFormatPassed):   
            if(not (outputFormat in availableOutputFormats)):
                print "ERREUR: le format de sortie specifie ('"+outputFormat+"') n'est pas reconnu."
                cmdLineErrorFound = True
    
        if(outputAlphaFormatPassed):   
            if(not (outputAlphaFormat in availableOutputFormats)):
                print "ERREUR: le format de sortie specifie pour les textures avec alpha ('"+outputAlphaFormat+"') n'est pas reconnu."
                cmdLineErrorFound = True
    
        if(outputJPEGQualityPassed):
            if(not isInt(outputJPEGQuality)):
                print "ERREUR: la qualite de compression JPEG doit etre un nombre entier."
                cmdLineErrorFound = True
            else:
                outputJPEGQuality = int(outputJPEGQuality)
                
                if((outputJPEGQuality<0) or (outputJPEGQuality>100)):
                    print "ERREUR: la qualite de compression JPEG doit etre comprise entre 0 et 100."
                    cmdLineErrorFound = True
                    
        if(outputRoofJPEGQualityPassed):
            if(not isInt(outputRoofJPEGQuality)):
                print "ERREUR: la qualite de compression JPEG pour les toits doit etre un nombre entier."
                cmdLineErrorFound = True
            else:
                outputRoofJPEGQuality = int(outputRoofJPEGQuality)
                
                if((outputRoofJPEGQuality<0) or (outputRoofJPEGQuality>100)):
                    print "ERREUR: la qualite de compression JPEG pour les toits doit etre comprise entre 0 et 100."
                    cmdLineErrorFound = True
                    
        if(maxSizePassed):                     
            if(not isInt(maxSize)):
                print "ERREUR: la taille maximum doit etre un nombre entier."
                cmdLineErrorFound = True
            else:
              maxSize = int(maxSize)
              if(maxSize<=0):
                  print "ERREUR: la taille maximum doit etre >0."
                  cmdLineErrorFound = True
              elif(not isInt(math.log(maxSize)/math.log(2))):
                  print "ERREUR: la taille maximum doit etre une puissance de 2."
                  cmdLineErrorFound = True                                            
            
        if(cmdLineErrorFound):
            printUsage(False)
            
        ###########################################
        #Initialisation du log HTML
        arTestResultsHandler = HTMLArTestResultsHandler()
        fileDateString = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mmin%Ssec")
        outputHTMLFilename = outputDirName+"/log_texturePublisher_"+fileDateString+".html"#"_"+machineName+"_"+userName+".html"        
        initHtmlOutputTestResult = TestResult("Initialisation du log de sortie HTML","Fichier : "+outputHTMLFilename)
        try:
            outputHTMLFile = open(outputHTMLFilename,"w")    
        except:
            initHtmlOutputTestResult += Result(False,ResultComment("Impossible d'ouvrir le fichier en ecriture."))
            arTestResultsHandler.addTestResult(_initHtmlOutputTestResult)
        if(not initHtmlOutputTestResult.getResultBool()):
           printUsage(False)          
        
        ###########################################
        #Execution    
        arTestResultCollection = publishTextureDirectory(inputDirName,outputDirName,outputResolutionString,outputFormat,outputAlphaFormat,outputJPEGQuality,outputRoofJPEGQuality,maxSizePassed,maxSize)
        
        ###########################################
        #Fin de l'execution et ecriture du log de sortie
        arTestResultsHandler.addArTestResultCollection(arTestResultCollection) 
        arTestResultsHandler.saveAsHTML(outputHTMLFile)
        outputHTMLFile.close()
        os.chmod(outputHTMLFilename,0777)
        
        if(arTestResultCollection.getResultBool()):
            print "Execution terminee correctement."
            sys.exit(0)
        else:
            print "L'execution ne s'est pas terminee correctement."
            print "Voir le log '"+outputHTMLFilename+"'"
            sys.exit(1)
        
    #Interruption clavier (CRTR+C...)
    except(KeyboardInterrupt):
        print ""
        print "> ERREUR: Interruption du programme par l'utilisateur !"
        print "> Provoque sortie du programme."
        sys.exit(1)
