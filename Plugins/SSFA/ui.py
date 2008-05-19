# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created: Tue May 13 11:35:10 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,334,358).size()).expandedTo(Dialog.minimumSizeHint()))

        self.treeWidget = QtGui.QTreeWidget(Dialog)
        self.treeWidget.setGeometry(QtCore.QRect(10,10,311,301))
        self.treeWidget.setIndentation(10)
        self.treeWidget.setAllColumnsShowFocus(False)
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setObjectName("treeWidget")

        self.modif = QtGui.QPushButton(Dialog)
        self.modif.setGeometry(QtCore.QRect(130,330,111,25))
        self.modif.setObjectName("modif")

        self.Close = QtGui.QPushButton(Dialog)
        self.Close.setGeometry(QtCore.QRect(250,330,75,25))
        self.Close.setObjectName("Close")

        self.refresh = QtGui.QPushButton(Dialog)
        self.refresh.setGeometry(QtCore.QRect(40,330,77,26))
        self.refresh.setObjectName("refresh")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.Close,QtCore.SIGNAL("clicked()"),Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "attributs selection", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(0,QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(1,QtGui.QApplication.translate("Dialog", "Value", None, QtGui.QApplication.UnicodeUTF8))
        self.modif.setText(QtGui.QApplication.translate("Dialog", "Modif attribut value", None, QtGui.QApplication.UnicodeUTF8))
        self.Close.setText(QtGui.QApplication.translate("Dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh.setText(QtGui.QApplication.translate("Dialog", "refresh", None, QtGui.QApplication.UnicodeUTF8))

