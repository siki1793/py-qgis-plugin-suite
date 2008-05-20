#!/usr/bin/env python
# -*- coding: iso-8859-1 -*- 

##########################################################
# computeRDBStats
# Auteur : B. GERVAIS
# 31/05/2007
# Ce programme permet de récupérer des stats 
# sur une RDB :
# - sur les hauteurs de cette RDB
# - sur l'utilisation des textures de sa TDB par cette RDB
# le résultat est donné sous la forme d'un fichier CSV
##########################################################

import osr
import sys
import string
import ogr
import re
import getopt



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
    print "rdb_computeStats [-h] -i rdb_name [-b 'xmin ymin xmax ymax'] [-t csv_tdb_stats_file] [-h csv_height_stats_file]"
    print "-b : use a BBOX for computation"
    print "-t : returns a CSV file with statistics on the TDB usage in the RDB"
    print "-h : returns a CSV file with statistics on the heights of buildings in the RDB"
    print "Warning : be careful that statistics on the TDB usage only works providing that:"
    print "          for every building, all walls use the same texture." 
    sys.exit(0)

    
def parseOptions(argv):
    # parse command line options
    try:
        opts, args = getopt.getopt(argv, "h", ["help"])
    except getopt.error, msg:
        print msg
        printUsage()        
  
    return args

def isFloat( str ):
    ok = 1
    try:
        float(str)
    except ValueError:
        ok = 0
    return ok
    
def getBboxFromString(bboxString):
    bboxStringSplit = bboxString.split(" ")
    if (len(bboxStringSplit)!=4):
        print "Error : unable to get BBOX from parameter '"+bboxString+"'"
        sys.exit(0)
    
    for value in bboxStringSplit:
        if(not isFloat(value)):
            print "Error in parameter '"+bboxString+"' : value '"+value+"' is not a number"
            sys.exit(0)
        
    xmin = float(bboxStringSplit[0])
    ymin = float(bboxStringSplit[1])
    xmax = float(bboxStringSplit[2])
    ymax = float(bboxStringSplit[3])
    
    return xmin,ymin,xmax,ymax


def getSQLStringFromBBOX(bbox):
    return "xmin(wkb_geometry)>="+str(bbox[0])+" and xmax(wkb_geometry)<="+str(bbox[2])+" and ymin(wkb_geometry)>="+str(bbox[1])+" and ymax(wkb_geometry)<="+str(bbox[3])


def retrieveTDBUsageStats(rdbName,csvStatsFileName,bbox):
    
    print "Retrieving TDB usage statistics..."
    
    #Ouverture RDB
    print "Opening RDB source '"+rdbName+"'..."
    
    try:
        rdbDataSource = ogr.Open(rdbName+" user=postgres")
    except:
        print "Error : unable to open RDB '"+rdbName+"'"
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
    print "Opening TDB source '"+tdbName+"'..."
    try:
        tdbDataSource = ogr.Open(tdbName+" user=postgres")
    except:
        print "Error : unable to open TDB '"+tdbName+"'"
        sys.exit(1)
    
    walltextureLayer = tdbDataSource.GetLayerByName("walltexture")
    if(walltextureLayer is None):
            print "Layer 'walltexture' was not found in TDB source"
            sys.exit(1)
    
    nbTextures = walltextureLayer.GetFeatureCount()
    print "Nb textures in TDB : "+str(nbTextures)
    
    #init bbox string pour restreindre la zone de calcul
    bboxString = ""
    if(bbox is not None):
        bboxString = "and "+getSQLStringFromBBOX(bbox)
    
    #init CSV
    csvFile = open(csvStatsFileName,"w")
    
    if(csvFile is None):
        print "Impossible to create CSV File '"+csvStatsFileName+"'"
        sys.exit(1)
    
    csvFile.write("'N° texture','filename','oldFileName','Nb times used'\n")
    
    #Récup des stats d'utilisation par texture 
    print "Retrieving stats for each texture"  
    pb=progressbarClass(nbTextures,"*")
    count = 0
    for i in range(nbTextures):
        
        walltextureLayer.SetNextByIndex(i)
        walltextureFeature = walltextureLayer.GetNextFeature()
        if(walltextureFeature is None):
            print "ERROR : could not retrieve info for texture number "+str(i)+"."
            sys.exit(1)
        
        fileName = walltextureFeature.filename
        oldTextureFileName = walltextureFeature.oldfilename
        fid = walltextureFeature.GetFID()
        
        #recup du nb de batiments utilisant la texture (du moins, l'utilisant sur leur 'premier' mur) 
        resultLayer = rdbDataSource.ExecuteSQL("select count(*) from block where (walltex[1]="+str(fid)+")"+bboxString)
        
        if(resultLayer is None):
            print "ERROR : could not retrieve stats for texture number "+str(i)+"."
            sys.exit(1)
        
        resultLayer.ResetReading()                
        resultFeature = resultLayer.GetNextFeature()
        
        if(resultFeature is None):
            print "ERROR : could not retrieve stats for texture number "+str(i)+"."
            sys.exit(1)        
        
        nbTimesUsed = resultFeature.count
                
        #print str(fid)+","+fileName+","+oldTextureFileName+","+str(nbTimesUsed)
        csvFile.write(str(fid)+","+fileName+","+oldTextureFileName+","+str(nbTimesUsed)+"\n")
        rdbDataSource.ReleaseResultSet(resultLayer)
        count += 1
        pb.progress(count)
    
    csvFile.close()

    tdbDataSource.Destroy()
    tdbDataSource = None
        
    rdbDataSource.Destroy()
    rdbDataSource = None    
    
    print "Done."    


def retrieveRDBBuildingHeightStats(rdbName,csvStatsFileName,bbox):
    
    print "Retrieving building height statistics..."
    
    #Ouverture RDB
    print "Opening RDB source '"+rdbName+"'..."
    
    try:
        rdbDataSource = ogr.Open(rdbName+" user=postgres")
    except:
        print "Error : unable to open RDB '"+rdbName+"'"
        sys.exit(1)
    
    if(rdbDataSource is None):
            print "RDB source not found"
            sys.exit(1)
    
    #init bbox string pour restreindre la zone de calcul
    bboxString = ""
    bboxStringWhere = ""
    if(bbox is not None):
        sqlString = getSQLStringFromBBOX(bbox)
        bboxString = "and "+sqlString
        bboxStringWhere = " where "+sqlString
    
    #Récup du nb d'emprises
    nbFeaturesResultLayer = rdbDataSource.ExecuteSQL("select count(*) from block"+bboxStringWhere)
    nbFeaturesResultLayer.ResetReading()
    nbFeaturesFeature = nbFeaturesResultLayer.GetNextFeature()       
    totalNbFeatures = nbFeaturesFeature.count    
    rdbDataSource.ReleaseResultSet(nbFeaturesResultLayer)
    print "Nb features in RDB = "+str(totalNbFeatures)
    
    #Récup des hauteurs min et max    
    minmaxHeightResultLayer = rdbDataSource.ExecuteSQL("select min(height),max(height) from block"+bboxStringWhere)
    minmaxHeightResultLayer.ResetReading()
    minmaxHeightResultFeature = minmaxHeightResultLayer.GetNextFeature()       
    minHeight = minmaxHeightResultFeature.min
    maxHeight = minmaxHeightResultFeature.max
    rdbDataSource.ReleaseResultSet(minmaxHeightResultLayer)
    print "Min Height = "+str(minHeight)
    print "Max Height = "+str(maxHeight)
    
    
    csvFile = open(csvStatsFileName,"w")    
    if(csvFile is None):
        print "Impossible to create CSV File '"+csvStatsFileName+"'"
        sys.exit(1)
    
    csvFile.write("'Hauteur','Nombre d'emprises','Pourcentage emprises'\n")
    
    #Récup des stats par hauteur
    print "Retrieving stats for each height"  
    heightRange = range(int(minHeight),int(maxHeight)+1)
    pb=progressbarClass(len(heightRange),"*")
    count = 0
    for i in heightRange:
        resultLayer = rdbDataSource.ExecuteSQL("select count(*) from block where (height>="+str(i)+" and height<"+str(i+1)+")"+bboxString)
        resultLayer.ResetReading()
        resultFeature = resultLayer.GetNextFeature()
        
        nbFeatures = resultFeature.count    
      
        #print str(i)+"\t"+oldTextureFileName+"\t"+str(nbTimesUsed)
        csvFile.write(str(i)+","+str(nbFeatures)+","+str(float(float(nbFeatures)/float(totalNbFeatures)))+"\n")
        rdbDataSource.ReleaseResultSet(resultLayer)
        count += 1
        pb.progress(count)
    
    csvFile.close()
        
    rdbDataSource.Destroy()
    rdbDataSource = None    
    
    print "Done."
    


   
if __name__ == '__main__':

    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:t:r:o:", ["help","input==","ressources==","output=="])
    except getopt.error, msg:
        print msg
        printUsage()

    # process options
    inputPassed = False
    inputFileName = ""
    tdbStatsOutputPassed = False
    tdbStatsOutputFileName = ""
    heightStatsOutputPassed = False
    heightStatsOutputFileName = ""
    bboxPassed = False
    bboxString = ""
        
    for opt, arg in opts:
        if opt in ("-i"):
            inputPassed = True
            inputFileName = arg
        if opt in ("-t"):
            tdbStatsOutputPassed = True
            tdbStatsOutputFileName = arg
        if opt in ("-h"):
            heightStatsOutputPassed = True
            heightStatsOutputFileName = arg
        if opt in ("-b"):
            bboxPassed = True
            bboxString = arg            

    if(not (inputPassed and (tdbStatsOutputPassed or heightStatsOutputPassed)) ):
        printUsage()
    else:
        
        bbox = None
        if(bboxPassed):
            bbox = getBboxFromString(bboxString)
            print "Using BBOX : xmin="+str(bbox[0])+" ymin="+str(bbox[1])+" xmax="+str(bbox[2])+" ymax="+str(bbox[3])
        
        if(tdbStatsOutputPassed):
            print ""
            retrieveTDBUsageStats(inputFileName,tdbStatsOutputFileName,bbox)
        
        if(heightStatsOutputPassed):        
            print ""            
            retrieveRDBBuildingHeightStats(inputFileName,heightStatsOutputFileName,bbox)
            
        sys.exit(0)
        