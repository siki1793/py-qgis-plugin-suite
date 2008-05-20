import os, sys
print "Suppression des fichiers...."
try:
    os.system("erase ui.py")
    pass
except:
    print "il n'existe pas de ui.py..."

curdir = sys.path[0]
#requet =  '"C:\Python25\pyuic4.bat" -o "' + curdir + '\ui.py" "' + curdir + '\untitled.ui"'
requet = '"C:\Python25\pyuic4.bat" -o ui.py uiFiles/untitled.ui'
print requet
os.system(requet)
