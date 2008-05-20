# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uiFiles/untitled.ui'
#
# Created: Tue May 20 15:28:20 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,355,462).size()).expandedTo(Dialog.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10,430,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.treeLayer = QtGui.QTreeWidget(Dialog)
        self.treeLayer.setGeometry(QtCore.QRect(10,100,331,331))
        self.treeLayer.setObjectName("treeLayer")

        self.layerMereCombo = QtGui.QComboBox(Dialog)
        self.layerMereCombo.setGeometry(QtCore.QRect(80,10,251,22))
        self.layerMereCombo.setObjectName("layerMereCombo")

        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10,10,71,21))
        self.label.setObjectName("label")

        self.layerFilleCombo = QtGui.QComboBox(Dialog)
        self.layerFilleCombo.setGeometry(QtCore.QRect(80,40,251,22))
        self.layerFilleCombo.setObjectName("layerFilleCombo")

        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10,40,71,21))
        self.label_2.setObjectName("label_2")

        self.ajouter = QtGui.QPushButton(Dialog)
        self.ajouter.setGeometry(QtCore.QRect(20,70,75,24))
        self.ajouter.setObjectName("ajouter")

        self.test = QtGui.QPushButton(Dialog)
        self.test.setGeometry(QtCore.QRect(100,70,75,24))
        self.test.setObjectName("test")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),Dialog.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.treeLayer.headerItem().setText(0,QtGui.QApplication.translate("Dialog", "Layers", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Layer mere : ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Layer fille : ", None, QtGui.QApplication.UnicodeUTF8))
        self.ajouter.setText(QtGui.QApplication.translate("Dialog", "Ajouter", None, QtGui.QApplication.UnicodeUTF8))
        self.test.setText(QtGui.QApplication.translate("Dialog", "Tester", None, QtGui.QApplication.UnicodeUTF8))

