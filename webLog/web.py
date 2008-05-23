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
