# List plugins installed :
import os, sys

version = "0.1"
print "List plugins Version  %s" %(version)
from xml.dom import minidom
dom = minidom.parse('plugins.xml')

section = dom.getElementsByTagName('Plugin')
for plugin in section:
     dir = plugin.getElementsByTagName('dir')[0].firstChild.data
     name = plugin.getElementsByTagName('name')[0].firstChild.data
     version = plugin.getElementsByTagName('version')[0].firstChild.data
     description = plugin.getElementsByTagName('description')[0].firstChild.data
     stabilite = plugin.getElementsByTagName('stabilite')[0].firstChild.data
     gui = plugin.getElementsByTagName('bool-gui')[0].firstChild.data
     
     print "-----------------------------------------------"
     print "Name : %s" % (name)
     print "Version : %s" % (version)
     print "Description : %s" % (description)
     if gui:
         print "GUI : Yes"
     else:
         print "GUI : No"
     print "Dir plugin : %s" % (dir)
     print "Stabilite : %s" % (stabilite)
print "---------------------END-----------------------"
