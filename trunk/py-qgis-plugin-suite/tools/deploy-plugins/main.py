#TODO: deux fonction debug, release pour pas tout importer
import os, sys
version = "0.1"

def extractConfig(dir_plugins,svn):
    print "Go install all plugin in %s" % (dir_plugins)
    
    #Liste des dossier dans le dossier
    os.chdir(dir_plugins)
    
    plugins = []
    
    for obj in os.listdir(os.curdir):
        if os.path.isdir(obj):
            plugins.append((obj,str(obj)))
    
    if svn:
        plugins = plugins[1:]
        
    return plugins

def copyPlugins(ListPlugPath,pathQGIS):
    if sys.platform == 'win32':
        for (plugins, pluginName) in ListPlugPath:
            try:
                os.system('erase /S /Q "%s"' % (pathQGIS + "\\" + pluginName))
            except:
                print "Premiere fois export : %s" % (pluginName) #FIXME: copie defecteuse
            os.system('xcopy /T /E "%s" "%s"' % (os.path.abspath(plugins),pathQGIS + "\\" + pluginName))

def applyConfig(path):
    from xml.dom import minidom
    dom = minidom.parse(path)
    dir_plugins = dom.getElementsByTagName('path')[0].firstChild.data
    svn = dom.getElementsByTagName('bool-svn')[0].firstChild.data
    pathQGIS = dom.getElementsByTagName('user-QGIS-path')[0].firstChild.data

    ListPlugPath = extractConfig(dir_plugins, svn)
    
    copyPlugins(ListPlugPath, pathQGIS)
    
if __name__=="__main__":
    print "Deploy plugins... version : %s" % (version)
    applyConfig('config.xml')
    print "SUCESS"