#!/usr/bin/env python
# -*- coding: iso-8859-1 -*- 

import osr
import sys
import string
import ogr
import re
import getopt
import gdal
import math
import os
import glob
import copy

from web import *

def printUsage():
    print "rdb_publisher -i tdb_name -r res -o out [-d directory]"
    sys.exit(0)

class progressbarClass: 
    def __init__(self, finalcount, progresschar=None):
        import sys
        self.finalcount=finalcount
        self.blockcount=0
        #
        # See if caller passed me a character to use on the
        # progress bar (like "*").  If not use the block
        # character that makes it look like a real progress
        # bar.
        #
        if not progresschar: self.block=chr(178)
        else:                self.block=progresschar
        #
        # Get pointer to sys.stdout so I can use the write/flush
        # methods to display the progress bar.
        #
        self.f=sys.stdout
        #
        # If the final count is zero, don't start the progress gauge
        #
        if not self.finalcount : return
        self.f.write('\n------------------ % Progress -------------------1\n')
        self.f.write('    1    2    3    4    5    6    7    8    9    0\n')
        self.f.write('----0----0----0----0----0----0----0----0----0----0\n')
        return

    def progress(self, count):
        #
        # Make sure I don't try to go off the end (e.g. >100%)
        #
        count=min(count, self.finalcount)
        #
        # If finalcount is zero, I'm done
        #
        if self.finalcount:
            percentcomplete=int(round(100*count/self.finalcount))
            if percentcomplete < 1: percentcomplete=1
        else:
            percentcomplete=100
            
        #print "percentcomplete=",percentcomplete
        blockcount=int(percentcomplete/2)
        #print "blockcount=",blockcount
        if blockcount > self.blockcount:
            for i in range(self.blockcount,blockcount):
                self.f.write(self.block)
                self.f.flush()
                
        if percentcomplete == 100: self.f.write("\n")
        self.blockcount=blockcount
        return

class connectPostGis:
    def __init__(self,nameDb,type="rdb"):
        self.__tr = TestResult("Connection Base PostGis","Trace d'execution de la connection à la base postGis")
        if nameDb == "":
            self.__tr +=  Result(False,ResultComment("Pas de connection donnee"))
        else:
            if type == "rdb":
                succes, connector = self.__testConnectionRdb(nameDb)
            elif type == "tdb":
                succes, connector = self.__testConnectionTdb(nameDb)
            else:
                self.__tr += Result(False,ResultComment("no type of postGis db is define"))
                sys.exit(1)
            
            if not succes:
                sys.exit(1)
            else:
                self.__con = connector
                self.__type = type
    
    def getTrace(self):
        return self.__tr
    
    def __testConnectionRdb(self,rdbName):
        try:
            rdbDataSource = ogr.Open(rdbName + " user=postgres")
        except:
            self.__tr += Result(False,ResultComment("Opening RDB source '%s'..." % (rdbName)),ResultComment("Error : unable to open RDB '%s'" % (rdbName)))
            return (False,None)
        
        if(rdbDataSource is None):
            self.__tr +=  Result(False,ResultComment("Opening RDB source '%s'..." % (rdbName)),ResultComment("RDB source not found"))
            return (False,None)
        else:
            self.__tr +=  Result(True,ResultComment("Opening RDB source '%s'..." % (rdbName)))
            
            return (True,rdbDataSource)
    
    def __testConnectionTdb(self,tdbName):
        #Récup du nombre de textures
        try:
            tdbDataSource = ogr.Open(tdbName+" user=postgres")
        except:
            self.__tr +=  Result(False,ResultComment("Opening TDB source '%s'..." % (tdbName)), ResultComment("Error : unable to open TDB '%s'" % (tdbName)))
            return (False,None)
        
        if(tdbDataSource is None):
            self.__tr +=  Result(False,ResultComment("Opening TDB source '%s'..." % (tdbName)), ResultComment("RDB source not found"))
            return (False,None)
        else:
            self.__tr +=  Result(False,ResultComment("Opening TDB source '%s'..." % (tdbName)))
            return (True,tdbDataSource)
    
    def convertToTdb(self):
        """Renvoie un bool si la conversion s'est bien passée
        Si il y a une erreur renvoie false et ne modif pas la
        connection avec la rdb"""
        
        if self.__type == "tdb":
            print "Conversion warning : no conversion needed"
            return True
        elif self.__type == "rdb":
            print "Conversion : rdb => tdb"
            infoLayer = self.__con.GetLayerByName("info")
            if(infoLayer is None):
                print "Layer 'info' was not found in RDB source"
                return False
    
            infoLayer.ResetReading()
            firstInfoFeature = infoLayer.GetNextFeature()
            tdbName = firstInfoFeature.tdb
            
            print "TDB used by RDB : " + tdbName
            succes, connector = self.__testConnectionTdb(tdbName)
            if succes:
                self.__con = connector
                self.__type = "tdb"
                return True
            else:
                return False
            
    def getConnection(self):
        return self.__con
    
    def isTdb(self):
        return (self.__type == "tdb")

class tdbTransformer:
    def __init__(self,connection):
        if connection.isTdb():
            self.__con = connection.getConnection()
        else:
            if connection.convertToTdb():
                self.__con = connection.getConnection()
            else:
                print "Error : can't convert your current connection in tdb connection"
                sys.exit(1) 
    
    def convertToPNG(self,outputDir,resolutionVoulu,directory="sources"):
        try:
            resolutionVoulu = float(resolutionVoulu)
        except:
            print "Error : la resolution passee n'est pas un nombre"
            sys.exit(1) 
            
        walltex = self.__getLayer("walltexture")
        idHeight = self.__getIdFeild("height", walltex)
        idWidth = self.__getIdFeild("width", walltex)
        idMeterHeight = self.__getIdFeild("meterheight", walltex)
        idMeterWidth = self.__getIdFeild("meterwidth", walltex)
        idFileName = self.__getIdFeild("filename", walltex)
        
        #On reste le provider
        walltex.ResetReading() 
        
        feature = walltex.GetNextFeature()
        
        self.__createArboOutputDir(outputDir)
        os.chdir(outputDir)
        
        #On prend la premiere feature pour voir la chemin de la tdb
        inputFileName = feature.GetFieldAsString(idFileName)
        
        tmp = ""
        for el in inputFileName.split("/")[:-1]:
            tmp += el + os.sep
        
        pathTdb = tmp
        
        pathTdb = os.path.normpath(pathTdb + os.sep  + directory)
        
        if self.__pathExists(pathTdb):
             print "Info : le chemin utiliser pour les images dans la tdb : %s" % (pathTdb)
        else:
            print "Error : le chemin utiliser pour les images dans la tdb [%s] n'est pas valide" % (pathTdb)
            sys.exit(1)
        
        pb=progressbarClass(walltex.GetFeatureCount(),"*")
        count = 0
        
        while(not (feature is None)):
            height = feature.GetFieos.path.normpath(ldAsDouble(idHeight))
            meterheight = feature.GetFieldAsDouble(idMeterHeight)
            width = feature.GetFieldAsDouble(idWidth)
            meterwidth = feature.GetFieldAsDouble(idMeterWidth)
            inputFileName = feature.GetFieldAsString(idFileName)
        
            resolutionY = meterheight / height
            resolutionX = meterwidth / width
            
            facteurX = resolutionX / resolutionVoulu
            facteurY = resolutionY / resolutionVoulu
            self.__transformTDBDossierOutput(inputFileName, outputDir, pathTdb, facteurX, facteurY)
        
            count += 1
            pb.progress(count)
            feature = walltex.GetNextFeature()
            #feature = None
        
        #On suppr la dossier tmp
        self.__cleanPath(os.path.normpath(outputDir + os.sep  + "tmp"))
            
    def __transformTDBDossierOutput(self,inputFileName, outputDir, pathTdb,facteurX, facteurY):
        nomFichier = inputFileName.split("/")[-1]
        
        os.chdir(outputDir)
        #On resize la texture
        #print "resizeTexture : %s => %s" % (os.path.normpath(pathTdb + os.sep + nomFichier), os.path.normpath(outputDir + os.sep + "tmp" + os.sep + nomFichier))
        resizeTexture(os.path.normpath(pathTdb + os.sep + nomFichier), os.path.normpath(outputDir + os.sep + "tmp" + os.sep + nomFichier), facteurX, facteurY)
        
        if os.path.exists(os.path.normpath(outputDir + os.sep + "tmp" + os.sep + nomFichier)):
            #print "resizeTexturePowerOfTwo : %s => %s" % (os.path.normpath(outputDir + os.sep + "tmp" + os.sep + nomFichier), os.path.normpath(outputDir + os.sep + nomFichier))
            #On fait le facteur de 2
            resizeTexturePowerOfTwo(os.path.normpath(outputDir + os.sep + "tmp" + os.sep + nomFichier),os.path.normpath(outputDir + os.sep + nomFichier))
        else:
            print "Error : le Premier zoom ne s'est pas bien passer, voir dans les logs"
            return Result("")
            
    def __pathExists(self,pathName):
        if(pathName==""):
            return False #car os.path.normPath renvoie "." quand on lui passe ""
        else:
            normPath = os.path.normpath(pathName)
            return (os.path.exists(normPath) or (len(glob.glob(normPath))>0))
    
    def __createArboOutputDir(self,dir):
        if self.__pathExists(dir):
            os.chdir(dir)
        else:
            print "Error : Le dossier de sortie n'existe de pas, veuillez le creer"
            sys.exit(1)
        if self.__pathExists(os.path.normpath(dir + os.sep + "tmp")):
            pass
        else:
            os.mkdir(os.path.normpath(dir + os.sep + "tmp"))
            
    def __getIdFeild(self,nameField,layer):
        id = layer.GetLayerDefn().GetFieldIndex(nameField)
        
        if(id is None):
            print "In layer '%s' haven't got '%s' field"
            sys.exit(1)
        
        return id
        
    def __getLayer(self,name):
        myLayer = self.__con.GetLayerByName(name)
    
        if(myLayer is None):
            print "Layer '%s' was not found in TDB source" % (name)
            sys.exit(1)
    
        return myLayer
    
    def __cleanPath(self,path):
        result = True
        for fileName in os.listdir(path):
            if os.path.isfile(fileName):
                try:
                    #print "Beuh! %s" % (fileName)
                    os.remove(os.path.normpath(path + os.sep + fileName))
                except:
                    print "Error : impossible de supprimer %s dans %s" % (fileName,path) 
            if os.path.isdir(fileName):
                print "Error : dossier tmp existant ?"
                result = False
    
        if result:
            try:
                os.rmdir(path)
            except:
                print "Erreur : ne dossier tmp n'a pas pu etre supprimer"


                
    
def resizeTexturePowerOfTwo(inputFileName,outputFileName,limitSize=False,maxSize=1024):
    gdal.AllRegister()
    gdalDataSet = gdal.Open(inputFileName)
    if gdalDataSet is None:
        print "Redimensionnement de l'image '"+inputFileName+"'",""
        print "ERREUR: impossible d'ouvrir l'image"
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
    
    resizeTextureWithSizes(inputFileName,outputFileName,newXSize2,newYSize2)
#    tr = resizeTextureWithSizes(inputFileName,outputFileName,newXSize2,newYSize2)
#    if( (newXSize2!=newXSize) or (newYSize2!=newYSize) ):
#        tr += Result(True,ResultComment(""),ResultComment("Warning: la texture '"+inputFileName+"' a ete resize de "+str(xsize)+"x"+str(ysize)+" vers "+str(newXSize2)+"x"+str(newYSize2)+" au lieu de "+str(newXSize)+"x"+str(newYSize)+"."))
#    
#    return tr

def resizeTexture(inputFileName,outputFileName,resizeFactorX,resizeFactorY):
    gdal.AllRegister()
    gdalDataSet = gdal.Open(inputFileName)
    if gdalDataSet is None:
        print "Redimensionnement de l'image '"+inputFileName+"'"
        print "ERREUR: impossible d'ouvrir l'image"
        sys.exit(1)
        
    xsize = gdalDataSet.RasterXSize
    ysize = gdalDataSet.RasterYSize
    del gdalDataSet    
    newXSize = max(1,math.floor(xsize*resizeFactorX+0.5))
    newYSize = max(1,math.floor(ysize*resizeFactorY+0.5))
    
    resizeTextureWithSizes(inputFileName,outputFileName,newXSize,newYSize)
#    return resizeTextureWithSizes(inputFileName,outputFileName,newXSize,newYSize)

def resizeTextureWithSizes(inputFileName,outputFileName,xsize,ysize):
    try:
        os.system("gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName+" > /dev/null 2>&1") #+" > /dev/null 2>&1"
    except:
        print "Fatal error : can't execute this command\n" + "gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName
        sys.exit(1)
   # print "gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName
        
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:r:o:d:", ["help","input==","ressource==","output==","directory=="])
    except getopt.error, msg:
        print msg
        printUsage()
    
    inputPassed = False
    inputFileName = ""
    tdbOutputDirPassed = False
    tdbOutputDir = ""
    resolutionPassed = False
    resolution = ""
    directoryPassed = False
    directory = ""
    
    for opt, arg in opts:
        if opt in ("-i"):
            inputPassed = True
            inputFileName = arg
        elif opt in ("-o"):
            tdbOutputDirPassed = True
            tdbOutputDir = arg
        elif opt in ("-r"):
            resolutionPassed = True
            resolution = arg
        elif opt in ("-d"):
            directoryPassed = True
            directory = arg
        else:
            printUsage()
    
    if(not (inputPassed and (tdbOutputDirPassed and resolutionPassed)) ):
        printUsage()
    else:
        arTestResultsHandler = HTMLArTestResultsHandler()
        fileDateString = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mmin%Ssec")
        outputHTMLFilename = tdbOutputDir+"/log_tdb_publisher_"+fileDateString+".html"#"_"+machineName+"_"+userName+".html"        
        initHtmlOutputTestResult = TestResult("Initialisation du log de sortie HTML","Fichier : "+outputHTMLFilename)
        arTestResultsHandler.addTestResult(initHtmlOutputTestResult)
        try:
            outputHTMLFile = open(outputHTMLFilename,"w")    
        except:
            initHtmlOutputTestResult += Result(False,ResultComment("Impossible d'ouvrir le fichier en ecriture."))
            arTestResultsHandler.addTestResult(_initHtmlOutputTestResult)
            print "Fatal error : ..."
        else:
            con = connectPostGis(inputFileName,"tdb")
            arTestResultsHandler.addTestResult(t.getTrace())
            if t.getTrace().getResultBool():
                t = tdbTransformer(con)
                if directoryPassed:
                    arTestResultsHandler.addArTestResultCollection(t.convertToPNG(tdbOutputDir,resolution,directory))
                else:
                    arTestResultsHandler.addArTestResultCollection(t.convertToPNG(tdbOutputDir,resolution))
            arTestResultsHandler.saveAsHTML(outputHTMLFile)
            outputHTMLFile.close()
            os.chmod(outputHTMLFilename,0777)
        
        print "Done."
        