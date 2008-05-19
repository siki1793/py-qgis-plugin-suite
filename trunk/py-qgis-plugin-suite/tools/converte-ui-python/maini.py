import os, sys
print "Suppression des fichiers...."
try:
    os.system("erase ui.py")
    os.system("erase CreateBuildClass.py")
    os.system("erase ModifBuildClass.py")
    pass
except:
    print "il n'existe pas de ui.py..."

curdir = sys.path[0]
#requet =  '"C:\Python25\pyuic4.bat" -o "' + curdir + '\ui.py" "' + curdir + '\untitled.ui"'
requet = '"C:\Python25\pyuic4.bat" -o ui.py uiFile/untitled.ui'
print requet
os.system(requet)
requet = '"C:\Python25\pyuic4.bat" -o CreateBuildClass.py uiFile/CreateBuildClass.ui'
print requet
os.system(requet)
requet = '"C:\Python25\pyuic4.bat" -o ModifBuildClass.py uiFile/ModifBuildClass.ui'
print requet
os.system(requet)
