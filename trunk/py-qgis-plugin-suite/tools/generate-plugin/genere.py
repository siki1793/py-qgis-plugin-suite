#---------------------------------
#
# Script de generation d'arbo
# python pour plugin
#
#--------------------------------

import os, sys

#Constantes
version = "0.1"

class generate:
    def __init__(self):
        self.enterInfo()
    
    def __repr__(self):
        t = "---- Description of your plug-in ----\n"
        t = t + "name : %s\n" % (self.name_pl)
        t = t + "description : %s\n" % (self.description_pl)
        t = t + "version : %s\n" % (self.version_pl)
        if self.b_icon:
            t = t + "icon : YES\n"
        else:
            t = t + "icon : NO\n"
        if self.b_gui:
            t = t + "GUI : YES\n"
        else:
            t = t + "GUI : NO\n"
        t = t + "Path generate plugin : %s" % (os.path.abspath(os.curdir))
        
        return t
    
    def enterInfo(self):
        self.name_pl = ""

        while(self.name_pl == ""):
            self.name_pl = raw_input("Name of plugin : ")
            if (self.name_pl == ""):
                print "You must specified the name of your plugin"
        
        self.description_pl = raw_input("Enter your description of your plugin ['No description'] : ")
        if self.description_pl == "":
            self.description_pl = "No description"

        self.version_pl = "0.1" #Version of plugin TODO: user can define he's version ?

        self.b_icon = (raw_input("Do you want a icon ? [y/n] : ")=="y")

        self.b_gui = (raw_input("Do you want a GUI for your plug-in ? [y/n] : ") =="y")

        path = raw_input("Path for your plugins dev [../../Plugins] : ")
    
        if path == "":
            os.chdir("../../Plugins")
        else:
            try:
                os.chdir(path)
            except:
                print "Error : invalid path plugin"
                sys.exit()

if __name__=="__main__":
    print "plugin manager - generate project - version %s" % (version)
    g = generate()
    print g


    



        