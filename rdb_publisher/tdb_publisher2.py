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
        tr = TestResult("Connection Base PostGis","Trace d'execution de la connection a la base postGis")
        
        self.__con = None
        self.__type = None
        
        if nameDb == "":
            tr +=  Result(False,ResultComment("Pas de connection donnee"))
        else:
            if type == "rdb":
                tr += self.__testConnectionRdb(nameDb)
            elif type == "tdb":
                tr += self.__testConnectionTdb(nameDb)
            else:
                tr += Result(False,ResultComment("no type of postGis db is define"))
        self.__tr = tr
    
    def getTrace(self):
        return self.__tr
    
    def getConnection(self):
        return self.__con
    
    def __testConnectionRdb(self,rdbName):
        tr = TestResult("Connection RDB","Trace d'execution de la connection a la base postGis")
        temp = True
        try:
            rdbDataSource = ogr.Open(rdbName + " user=postgres")
        except:
            temp = False
        tr += Result(temp,ResultComment("Error : unable to open RDB '%s'" % (rdbName)))
        if temp:
            tr +=  Result(rdbDataSource != None,ResultComment("RDB source not found"))
            self.__con = rdbDataSource
            self.__type = "rdb"
        
        return tr
            
    def __testConnectionTdb(self,tdbName):
        tr = TestResult("Connection RDB","Trace d'execution de la connection a la base postGis")
        temp = True
        try:
            tdbDataSource = ogr.Open(tdbName+" user=postgres")
        except:
            temp = False
        tr +=  Result(temp,ResultComment("Error : unable to open TDB '%s'" % (tdbName)))
        if(temp):
            tr +=  Result(tdbDataSource != None,ResultComment("RDB source not found"))
            self.__con = tdbDataSource
            self.__type = "tdb"
        
        return tr
    
    def convertToTdb(self):
        tr = TestResult("Conversion vers TDB","Trace d'execution de la convertion a la tdb postGis")
        if self.__con == None:
            tr += Result(False,ResultComment("Pas de connection initialisee correctement"))
            return tr
        if self.__type == "tdb":
            tr += Result(True,ResultComment("Conversion warning : no conversion needed"))
            return tr
        elif self.__type == "rdb":
            tr += Result(True,ResultComment("Conversion : rdb => tdb"))
            infoLayer = self.__con.GetLayerByName("info")
            if(infoLayer is None):
                tr +=  Result(False,ResultComment("Conversion rdb error"),ResultComment("Layer 'info' was not found in RDB source"))
                return tr
            infoLayer.ResetReading()
            firstInfoFeature = infoLayer.GetNextFeature()
            tdbName = firstInfoFeature.tdb
            
            tr +=  Result(True,ResultComment("TDB used by RDB : " + tdbName))
            tr += self.__testConnectionTdb(tdbName)
            return tr
            
    def getConnection(self):
        return self.__con
    
    def isTdb(self):
        return (self.__type == "tdb")

class tdbTransformer:
    def __init__(self,connection):
        self.__con = None
        
        tr = TestResult("initialisation tdbTransformer","")
        if connection.isTdb():
            self.__con = connection.getConnection()
        else:
            tr += connection.convertToTdb()
            tr += Result(tr.getResultBool(),ResultComment("can't convert your current connection in tdb connection"))
            self.__con = connection.getConnection()
        self.__initTr = tr
    def getTraceInit(self):
        return self.__initTr
    
    def convertToPNG(self,outputDir,resolutionVoulu,directory):
        tr = ArTestResult("Convert tdb in PNG","")
        tr2 = TestResult("Initialisation convertion PNG","",self.__con != None,ResultComment("Pas de conection correctement initialisee"))
        if self.__con == None:
            return tr
        try:
            resolutionVoulu = float(resolutionVoulu)
        except:
            tr2 += Result(False,ResultComment("Error : la resolution passee n'est pas un nombre"))
            tr.addTestResult(tr2)
            return tr
        
        tr2 += Result(True,ResultComment("Error : la resolution passee n'est pas un nombre"))
        tr.addTestResult(tr2)
        if directory=="":
            directory = "sources"
        
        #On cherche les layers
        walltex = self.__getLayer("walltexture",tr)
        
        if not tr.getResultBool(): #Mal passer
            return tr
        
        #Les Ids
        tr2 = TestResult("Calcul des id pour les differentes info qui nous interresse","")
        idHeight = self.__getIdFeild("height", walltex,tr2)
        idWidth = self.__getIdFeild("width", walltex,tr2)
        idMeterHeight = self.__getIdFeild("meterheight", walltex,tr2)
        idMeterWidth = self.__getIdFeild("meterwidth", walltex,tr2)
        idFileName = self.__getIdFeild("filename", walltex,tr2)
        
        tr.addTestResult(tr2)
        
        if not tr.getResultBool(): #Mal passer
            return tr
        #On reste le provider
        walltex.ResetReading() 
        
        #On initialisa la boucle (while)
        feature = walltex.GetNextFeature()
        
        #On cree larboraisance
        self.__createArboOutputDir(outputDir,tr)
        if not tr.getResultBool(): #Mal passer
            return tr
        
        os.chdir(outputDir)
        
        #On prend la premiere feature pour voir la chemin de la tdb
        inputFileName = feature.GetFieldAsString(idFileName)
        
        #On cherche le chemin de la tdb a partir de la table
        tmp = ""
        for el in inputFileName.split("/")[:-1]:
            tmp += el + os.sep
        
        pathTdb = tmp
        
        pathTdb = os.path.normpath(pathTdb + os.sep  + directory)
        
        tr2 = TestResult("Extraction du chemin de la tdb","Info : le chemin utiliser pour les images dans la tdb : %s" % (pathTdb), self.__pathExists(pathTdb), ResultComment("le chemin utiliser pour les images dans la tdb [%s] n'est pas valide" % (pathTdb)))
        tr.addTestResult(tr2)
        if not tr.getResultBool():
           return tr
       
       #On initialise la barre de progression.
        pb=progressbarClass(walltex.GetFeatureCount(),"*")
        count = 0
        
        while(not (feature is None)): #On boucle
            
            #On prend les differentes valeurs dans la tdb pour la feature
            height = feature.GetFieldAsDouble(idHeight)
            meterheight = feature.GetFieldAsDouble(idMeterHeight)
            width = feature.GetFieldAsDouble(idWidth)
            meterwidth = feature.GetFieldAsDouble(idMeterWidth)
            inputFileName = feature.GetFieldAsString(idFileName)
        
            #On calcul les differentes resolution ...
            resolutionY = meterheight / height
            resolutionX = meterwidth / width
            # ... et les facteurs par rapport a la resolution voulu
            facteurX = resolutionX / resolutionVoulu
            facteurY = resolutionY / resolutionVoulu
            
            tr.addTestResult(self.__transformTDBDossierOutput(inputFileName, outputDir, pathTdb, facteurX, facteurY))
        
            #On incremente la progress Barre et positionne feature sur la feature suivante
            count += 1
            pb.progress(count)
            feature = walltex.GetNextFeature()
        
        #On suppr la dossier tmp
        self.__cleanPath(os.path.normpath(outputDir + os.sep  + "tmp"))
            
    def __transformTDBDossierOutput(self,inputFileName, outputDir, pathTdb,facteurX, facteurY):
        
        #On recupere le nom du fichier
        nomFichier = inputFileName.split("/")[-1]
        
        tr = TestResult("Traitement de l'image " + nomFichier, "")
        
        os.chdir(outputDir)
        #On resize la texture
        #print "resizeTexture : %s => %s" % (os.path.normpath(pathTdb + os.sep + nomFichier), os.path.normpath(outputDir + os.sep + "tmp" + os.sep + nomFichier))
        tr += resizeTexture(os.path.normpath(pathTdb + os.sep + nomFichier), os.path.normpath(outputDir + os.sep + "tmp" + os.sep + nomFichier), facteurX, facteurY)
        
        #TODO: Est ce que le deuxieme test est neccessaire ?
        if tr.getResultBool() and os.path.exists(os.path.normpath(outputDir + os.sep + "tmp" + os.sep + nomFichier)):
            #On fait le facteur de 2
            tr += resizeTexturePowerOfTwo(os.path.normpath(outputDir + os.sep + "tmp" + os.sep + nomFichier),os.path.normpath(outputDir + os.sep + nomFichier))
        else:
            tr += Result(False,ResultComment("Error : le Premier zoom ne s'est pas bien passer, voir dans les logs"))
        
        return tr 
            
    def __pathExists(self,pathName):
        if(pathName==""):
            return False #car os.path.normPath renvoie "." quand on lui passe ""
        else:
            normPath = os.path.normpath(pathName)
            return (os.path.exists(normPath) or (len(glob.glob(normPath))>0))
    
    def __createArboOutputDir(self,dir,trace):
        tr = TestResult("Cree les dossiers temporaire" ,"",self.__pathExists(dir),ResultComment("Error : Le dossier de sortie n'existe de pas, veuillez le creer"))
        if tr.getResultBool():
            os.chdir(dir)
        else:
            trace.addTestResult(tr)
            return
        
        if self.__pathExists(os.path.normpath(dir + os.sep + "tmp")):
            pass
        else:
            os.mkdir(os.path.normpath(dir + os.sep + "tmp"))
        
        trace.addTestResult(tr)
            
    def __getIdFeild(self,nameField,layer,trace):
        id = layer.GetLayerDefn().GetFieldIndex(nameField)
        trace += TestResult("Cherche le numero de l'index pour %s" % (nameField), "", id != None, ResultComment("haven't got '%s' field" % (nameField)))
        return id
        
    def __getLayer(self,name, tr):
        myLayer = self.__con.GetLayerByName(name)
        tr.addTestResult(TestResult("Prend la layer "+ name, "", myLayer is not None, ResultComment("Layer '%s' was not found in TDB source" % (name))))
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
    tr = resizeTextureWithSizes(inputFileName,outputFileName,newXSize2,newYSize2)
    
    if( (newXSize2!=newXSize) or (newYSize2!=newYSize) ):
        tr += Result(True,ResultComment(""),ResultComment("Warning: la texture '"+inputFileName+"' a ete resize de "+str(xsize)+"x"+str(ysize)+" vers "+str(newXSize2)+"x"+str(newYSize2)+" au lieu de "+str(newXSize)+"x"+str(newYSize)+"."))
    return tr 

def resizeTexture(inputFileName,outputFileName,resizeFactorX,resizeFactorY):
    gdal.AllRegister()
    gdalDataSet = gdal.Open(inputFileName)
    if gdalDataSet is None:
        tr = TestResult("Redimensionnement de l'image '"+inputFileName+"'","")
        tr += Result(False,ResultComment("ERREUR: impossible d'ouvrir l'image"))
        return tr   
        
    xsize = gdalDataSet.RasterXSize
    ysize = gdalDataSet.RasterYSize
    del gdalDataSet    
    newXSize = max(1,math.floor(xsize*resizeFactorX+0.5))
    newYSize = max(1,math.floor(ysize*resizeFactorY+0.5))
    
    return resizeTextureWithSizes(inputFileName,outputFileName,newXSize,newYSize)

def resizeTextureWithSizes(inputFileName,outputFileName,xsize,ysize):
    ok=True
    try:
        os.system("gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName+" > /dev/null 2>&1") #+" > /dev/null 2>&1"
    except:
        ok=False
    return Result(ok,ResultComment("Fatal error : can't execute this command\n" + "gdal_zoomPVM -of PNG -s "+str(xsize)+" "+str(ysize)+" -m quality -in "+inputFileName+" -out "+outputFileName))
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
            #Initialisation de la connection
            connec = connectPostGis(inputFileName,"tdb")
            arTestResultsHandler.addTestResult(connec.getTrace())
            #L'initialisation du tdb Transfromer avec la connection deja initialisee
            tdbT = tdbTransformer(connec)
            arTestResultsHandler.addTestResult(tdbT.getTraceInit())
            #Tranformation!!!
            trTrans = tdbT.convertToPNG(tdbOutputDir,resolution,directory)
            arTestResultsHandler.addArTestResultCollection(trTrans)
            #Ecriture du log
            arTestResultsHandler.saveAsHTML(outputHTMLFile)
            outputHTMLFile.close()
            os.chmod(outputHTMLFilename,0777)
            if trTrans.getResultBool():
                print "Done."
                sys.exit(0)
            else:
                print "L'execution ne s'est pas terminee correctement."
                print "Voir le log '"+outputHTMLFilename+"'"
                sys.exit(1)