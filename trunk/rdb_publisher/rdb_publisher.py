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

#FIXME: faire verife que les valeurs de outDir sont des chemins

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


def printUsage():
    print "rdb_publisher -i rdb_name -r res -o out"
    sys.exit(0)


def retrieveTDB(rdbName,resolutionVoulu,outputDir):
    
    #Ouverture RDB
    print "Opening RDB source '%s'..." % (rdbName)
    
    try:
        rdbDataSource = ogr.Open(rdbName + " user=postgres")
    except:
        print "Error : unable to open RDB '%s'" % (rdbName)
        sys.exit(1)
        
    if(rdbDataSource is None):
            print "RDB source not found"
            sys.exit(1)
    
    #Récup du nom de la TDB
    infoLayer = rdbDataSource.GetLayerByName("info")
    if(infoLayer is None):
            print "Layer 'info' was not found in RDB source"
            sys.exit(1)
    
    infoLayer.ResetReading()
    firstInfoFeature = infoLayer.GetNextFeature()
    tdbName = firstInfoFeature.tdb
    print "TDB used by RDB : "+tdbName
    
    #Récup du nombre de textures
    print "Opening TDB source '%s'..." % (tdbName)
    try:
        tdbDataSource = ogr.Open(tdbName+" user=postgres")
    except:
        print "Error : unable to open TDB '%s'" % (tdbName)
        sys.exit(1)
    #On a bien le pointeur sur la tdb
    #On va sur la table walltexture
    walltextureLayer = tdbDataSource.GetLayerByName("walltexture")
    
    if(walltextureLayer is None):
            print "Layer 'walltexture' was not found in TDB source"
            sys.exit(1)
    
    nbTextures = walltextureLayer.GetFeatureCount()
    print "Nb textures in TDB : %s" % (nbTextures)
    
    idHeight = walltextureLayer.GetLayerDefn().GetFieldIndex("height")
    idMeterHeight = walltextureLayer.GetLayerDefn().GetFieldIndex("meterheight")
    idFileName = walltextureLayer.GetLayerDefn().GetFieldIndex("filename")
    
    if (idHeight is None):
        print "In layer 'walltexture' not have 'height' field"
        sys.exit(1)
    else:
        print "info : id of Height : %s" % (idHeight)
    if (idMeterHeight is None):
        print "In layer 'walltexture' not have 'meterheight' field"
        sys.exit(1)
    else:
        print "info : id of MeterHeight : %s" % (idMeterHeight)
    
    pb=progressbarClass(nbTextures,"*")
    count = 0
    
    #La boucle
    for i in range(nbTextures):
        walltextureLayer.SetNextByIndex(i)
        walltextureFeature = walltextureLayer.GetNextFeature()
        
        #Verif que l'on a pas rien
        if(walltextureFeature is None):
            print "ERROR : could not retrieve info for texture number "+str(i)+"."
            sys.exit(1)
            
        height = walltextureFeature.GetFieldAsDouble(idHeight)
        meterheight = walltextureFeature.GetFieldAsDouble(idMeterHeight)
        inputFileName = walltextureFeature.GetFieldAsDouble(idFileName)
        
        resolution = meterheight / height
        
        facteur = resolutionVoulu / resolution
        
        transformTDBDossierOutput(inputFileName, outputDir, facteur)
        
        count += 1
        pb.progress(count) 
    
    print "Done."
    
    
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
        tr = TestResult("Redimensionnement de l'image '"+inputFileName+"'","")
        tr += Result(False,ResultComment("ERREUR: impossible d'ouvrir l'image"))
        return tr    
    xsize = gdalDataSet.RasterXSize
    ysize = gdalDataSet.RasterYSize
    del gdalDataSet    
    newXSize = max(1,math.floor(xsize*resizeFactor+0.5))
    newYSize = max(1,math.floor(ysize*resizeFactor+0.5))
    
    resizeTextureWithSizes(inputFileName,outputFileName,newXSize,newYSize)
#    return resizeTextureWithSizes(inputFileName,outputFileName,newXSize,newYSize)

def createArboOutput(outputDir):
    if os.path.exists(outputDir):
        print "Info : le dossier de sortie n'existe pas il sera donc cree"
        try:
            os.mkdir(outputDir)
        except:
            print "FATAL ERROR : ne peut pas cree le dossier de sortie"
            sys.exit(1)
    #On cree un dossier tmp
    os.chdir(outputDir)
    os.mkdir("tmp")
    
        

def transformTDBDossierOutput(inputFileName, outputDir, resizeFactor):
    #On calcul le nom du fichier
    nomFichier = inputFileName.split("//")[-1]
    os.chdir(outputDir)
    
    #On resize la texture
    resizeTexture(inputFileName, "tmp" + os.sep + nomFichier, resizeFactor)
    
    #On fait le facteur de 2
    resizeTexturePowerOfTwo("tmp" + os.sep + nomFichier, nomFichier)
    

def resizeTextureWithSizes(inputFileName,outputFileName,xsize,ysize):
    try:
        os.system("gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName)
    except:
        print "Fatal error : can't execute this command\n" + "gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName
        sys.exit(1)
        
        
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
        createArboOutput(tdbOutputDir)
        retrieveTDB(inputFileName)