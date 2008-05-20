# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uiFile/untitled.ui'
#
# Created: Tue May 20 11:24:45 2008
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

        self.treeFiltre = QtGui.QTreeWidget(Dialog)
        self.treeFiltre.setGeometry(QtCore.QRect(10,130,331,301))
        self.treeFiltre.setObjectName("treeFiltre")

        self.layerCombo = QtGui.QComboBox(Dialog)
        self.layerCombo.setGeometry(QtCore.QRect(80,10,251,22))
        self.layerCombo.setObjectName("layerCombo")

        self.attributeCombo = QtGui.QComboBox(Dialog)
        self.attributeCombo.setGeometry(QtCore.QRect(80,40,251,22))
        self.attributeCombo.setObjectName("attributeCombo")

        self.operator = QtGui.QComboBox(Dialog)
        self.operator.setGeometry(QtCore.QRect(80,70,121,22))
        self.operator.setObjectName("operator")

        self.valueLine = QtGui.QLineEdit(Dialog)
        self.valueLine.setGeometry(QtCore.QRect(80,100,121,20))
        self.valueLine.setObjectName("valueLine")

        self.ajouterFiltre = QtGui.QPushButton(Dialog)
        self.ajouterFiltre.setGeometry(QtCore.QRect(220,70,101,26))
        self.ajouterFiltre.setObjectName("ajouterFiltre")

        self.appliquerFiltre = QtGui.QPushButton(Dialog)
        self.appliquerFiltre.setGeometry(QtCore.QRect(220,100,101,26))
        self.appliquerFiltre.setObjectName("appliquerFiltre")

        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10,10,71,21))
        self.label.setObjectName("label")

        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10,40,71,21))
        self.label_2.setObjectName("label_2")

        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(10,70,51,21))
        self.label_3.setObjectName("label_3")

        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(10,100,51,21))
        self.label_4.setObjectName("label_4")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),Dialog.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.treeFiltre.headerItem().setText(0,QtGui.QApplication.translate("Dialog", "Attribute", None, QtGui.QApplication.UnicodeUTF8))
        self.treeFiltre.headerItem().setText(1,QtGui.QApplication.translate("Dialog", "Operator", None, QtGui.QApplication.UnicodeUTF8))
        self.treeFiltre.headerItem().setText(2,QtGui.QApplication.translate("Dialog", "Value", None, QtGui.QApplication.UnicodeUTF8))
        self.ajouterFiltre.setText(QtGui.QApplication.translate("Dialog", "Ajouter filtre", None, QtGui.QApplication.UnicodeUTF8))
        self.appliquerFiltre.setText(QtGui.QApplication.translate("Dialog", "Appliquer filtre", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Layer : ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Attribute :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Operator :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Value :", None, QtGui.QApplication.UnicodeUTF8))

