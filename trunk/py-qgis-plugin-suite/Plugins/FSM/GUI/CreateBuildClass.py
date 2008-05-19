# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uiFile/CreateBuildClass.ui'
#
# Created: Wed May 14 17:05:21 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_CreateBuildClass(object):
    def setupUi(self, CreateBuildClass):
        CreateBuildClass.setObjectName("CreateBuildClass")
        CreateBuildClass.resize(QtCore.QSize(QtCore.QRect(0,0,244,76).size()).expandedTo(CreateBuildClass.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(CreateBuildClass)
        self.buttonBox.setGeometry(QtCore.QRect(-120,40,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.label = QtGui.QLabel(CreateBuildClass)
        self.label.setGeometry(QtCore.QRect(10,10,105,16))
        self.label.setObjectName("label")

        self.lineEdit = QtGui.QLineEdit(CreateBuildClass)
        self.lineEdit.setGeometry(QtCore.QRect(120,10,113,20))
        self.lineEdit.setObjectName("lineEdit")

        self.retranslateUi(CreateBuildClass)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),CreateBuildClass.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),CreateBuildClass.reject)
        QtCore.QMetaObject.connectSlotsByName(CreateBuildClass)

    def retranslateUi(self, CreateBuildClass):
        CreateBuildClass.setWindowTitle(QtGui.QApplication.translate("CreateBuildClass", "Creer une building class", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("CreateBuildClass", "Nom de la build class :", None, QtGui.QApplication.UnicodeUTF8))

