#---------------------------------
#
# Script de generation d'arbo
# python pour plugin
#
#--------------------------------

import os, sys

#Constantes
version = "0.1"

#FIXME: faire avec approche objet

def resume():
    print "---- Description of your plug-in ----"
    print "name : %s" % (name_pl)
    print "description : %s" % (description_pl)
    print "version : %s" % (version)
    if b_gui:
        print "icon : YES"
    else:
        print "icon : NO"
    if b_gui:
        print "GUI : YES"
    else:
        print "GUI : NO"
def enterInfo():
    name_pl = ""

    while(name_pl == ""):
        name_pl = raw_input("Name of plugin : ")
        if (name_pl == ""):
            print "You must specified the name of your plugin"
        
    description_pl = raw_input("Enter your description of your plugin ['No description'] : ")
    if description_pl == "":
        description_pl = "No description"

    version_pl = "0.1" #Version of plugin TODO: user can define he's version ?

    b_icon = (raw_input("Do you want a icon ? [y/n] : ")=="y")

    b_gui = (raw_input("Do you want a GUI for your plug-in ? [y/n] : ") =="y")



if __name__=="__main__":
    print "plugin manager - generate project - version %s" % (version)
    enterInfo()
    resume()


    



        