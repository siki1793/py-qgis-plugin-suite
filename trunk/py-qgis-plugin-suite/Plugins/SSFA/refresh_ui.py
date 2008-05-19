import os, sys
print "Suppression des fichiers...."
try:
    #os.system("erase ui.py")
    pass
except:
    print "il n'existe pas de ui.py..."

curdir = sys.path[0]
#requet =  '"C:\Python25\pyuic4.bat" -o "' + curdir + '\ui.py" "' + curdir + '\untitled.ui"'
requet = '"C:\Python25\pyuic4.bat" -o ui.py untitled.ui'
print requet
os.system(requet)
requet2 = '"C:\Python25\pyuic4.bat" -o dialog_modif.py FentreModif.ui'
print requet2
os.system(requet2)