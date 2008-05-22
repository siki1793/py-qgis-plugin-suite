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


def printUsage():
    print "rdb_publisher -i tdb_name -r res -o out"
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
        if nameDb == "":
            print "Error : no connection give ..."
            sys.exit(1)
        else:
            if type == "rdb":
                succes, connector = self.__testConnectionRdb(nameDb)
            elif type == "tdb":
                succes, connector = self.__testConnectionTdb(nameDb)
            else:
                print "Error : no type of postGis db is define"
                sys.exit(1)
            
            if not succes:
                sys.exit(1)
            else:
                self.__con = connector
                self.__type = type
        
    def __testConnectionRdb(self,rdbName):
        print "Opening RDB source '%s'..." % (rdbName)
        try:
            rdbDataSource = ogr.Open(rdbName + " user=postgres")
        except:
            print "Error : unable to open RDB '%s'" % (rdbName)
            return (False,None)
        
        if(rdbDataSource is None):
            print "RDB source not found"
            return (False,None)
        
        else:
            return (True,rdbDataSource)
    
    def __testConnectionTdb(self,tdbName):
        #R�cup du nombre de textures
        print "Opening TDB source '%s'..." % (tdbName)
        try:
            tdbDataSource = ogr.Open(tdbName+" user=postgres")
        except:
            print "Error : unable to open TDB '%s'" % (tdbName)
            return (False,None)
        
        if(tdbDataSource is None):
            print "RDB source not found"
            return (False,None)
        else:
            return (True,tdbDataSource)
    
    def convertToTdb(self):
        """Renvoie un bool si la conversion s'est bien pass�e
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
    
    def convertToPNG(self,outputDir,resolutionVoulu):
        try:
            resolutionVoulu = float(resolutionVoulu)
        except:
            print "Error : la resolution passee n'est pas un nombre"
            sys.exit(1) 
            
        walltex = self.__getLayer("walltexture")
        idHeight = self.__getIdFeild("height", walltex)
        idMeterHeight = self.__getIdFeild("meterheight", walltex)
        idFileName = self.__getIdFeild("filename", walltex)
        
        pb=progressbarClass(walltex.GetFeatureCount(),"*")
        count = 0
        
        #On reste le provider
        walltex.ResetReading() 
        
        feature = walltex.GetNextFeature()
        
        self.__createArboOutputDir(outputDir)
        os.chdir(outputDir)
        
        while(not (feature is None)):
            height = feature.GetFieldAsDouble(idHeight)
            meterheight = feature.GetFieldAsDouble(idMeterHeight)
            inputFileName = feature.GetFieldAsString(idFileName)
        
            resolution = meterheight / height
            
            facteur = resolution / resolutionVoulu
            #print "la resolution img : %s et la facteur voulu %s" % (resolution,facteur)
            self.__transformTDBDossierOutput(inputFileName, outputDir, facteur)
        
            count += 1
            pb.progress(count)
            feature = walltex.GetNextFeature()
            #feature = None
            
    def __transformTDBDossierOutput(self,inputFileName, outputDir, resizeFactor):
        nomFichier = inputFileName.split("/")[-1]
        pathTdb = inputFileName.split("/")[:-1]
        
        tmp = ""
        for el in pathTdb:
            tmp += el + os.sep
        
        pathTdb = tmp
        #On resize la texture
        resizeTexture(os.path.normpath(pathTdb + "sources" + os.sep + nomFichier), os.path.normpath("tmp" + os.sep + nomFichier), resizeFactor)
    
        #On fait le facteur de 2
        resizeTexturePowerOfTwo(os.path.normpath("tmp" + os.sep + nomFichier), nomFichier)
        
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

def resizeTexture(inputFileName,outputFileName,resizeFactor):
    gdal.AllRegister()
    gdalDataSet = gdal.Open(inputFileName)
    if gdalDataSet is None:
        print "Redimensionnement de l'image '"+inputFileName+"'"
        print "ERREUR: impossible d'ouvrir l'image"
        sys.exit(1)
        
    xsize = gdalDataSet.RasterXSize
    ysize = gdalDataSet.RasterYSize
    del gdalDataSet    
    newXSize = max(1,math.floor(xsize*resizeFactor+0.5))
    newYSize = max(1,math.floor(ysize*resizeFactor+0.5))
    
    resizeTextureWithSizes(inputFileName,outputFileName,newXSize,newYSize)
#    return resizeTextureWithSizes(inputFileName,outputFileName,newXSize,newYSize)

    

def resizeTextureWithSizes(inputFileName,outputFileName,xsize,ysize):
    try:
        os.system("gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName+" > /dev/null 2>&1")
    except:
        print "Fatal error : can't execute this command\n" + "gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName
        sys.exit(1)
   # print "gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName
        
        
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:r:o:", ["help","input==","ressource==","output=="])
    except getopt.error, msg:
        print msg
        printUsage()
    
    inputPassed = False
    inputFileName = ""
    tdbOutputDirPassed = False
    tdbOutputDir = ""
    resolutionPassed = False
    resolution = ""
    
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
    
    if(not (inputPassed and (tdbOutputDirPassed and resolutionPassed)) ):
        printUsage()
    else:
        t=tdbTransformer(connectPostGis(inputFileName,"tdb"))
        t.convertToPNG(tdbOutputDir,resolution)
        print "Done."
        