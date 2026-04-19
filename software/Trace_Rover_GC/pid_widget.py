# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pid_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFormLayout,
    QGridLayout, QLabel, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(250, 355)
        Form.setMinimumSize(QSize(250, 355))
        Form.setBaseSize(QSize(250, 355))
        self.verticalLayoutWidget_2 = QWidget(Form)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(10, 10, 231, 331))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.pid_info_label = QLabel(self.verticalLayoutWidget_2)
        self.pid_info_label.setObjectName(u"pid_info_label")
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.pid_info_label.setFont(font)

        self.verticalLayout_2.addWidget(self.pid_info_label)

        self.comboBox = QComboBox(self.verticalLayoutWidget_2)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.verticalLayout_2.addWidget(self.comboBox)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.delta_label = QLabel(self.verticalLayoutWidget_2)
        self.delta_label.setObjectName(u"delta_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.delta_label)

        self.delta_val_label = QLabel(self.verticalLayoutWidget_2)
        self.delta_val_label.setObjectName(u"delta_val_label")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.delta_val_label)

        self.delta_d_label = QLabel(self.verticalLayoutWidget_2)
        self.delta_d_label.setObjectName(u"delta_d_label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.delta_d_label)

        self.delta_d_val_label = QLabel(self.verticalLayoutWidget_2)
        self.delta_d_val_label.setObjectName(u"delta_d_val_label")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.delta_d_val_label)

        self.delta_i_label = QLabel(self.verticalLayoutWidget_2)
        self.delta_i_label.setObjectName(u"delta_i_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.delta_i_label)

        self.delta_i_val_label = QLabel(self.verticalLayoutWidget_2)
        self.delta_i_val_label.setObjectName(u"delta_i_val_label")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.delta_i_val_label)

        self.kp_label = QLabel(self.verticalLayoutWidget_2)
        self.kp_label.setObjectName(u"kp_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.kp_label)

        self.kp_Box = QDoubleSpinBox(self.verticalLayoutWidget_2)
        self.kp_Box.setObjectName(u"kp_Box")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.kp_Box)

        self.ki_label = QLabel(self.verticalLayoutWidget_2)
        self.ki_label.setObjectName(u"ki_label")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.ki_label)

        self.ki_box = QDoubleSpinBox(self.verticalLayoutWidget_2)
        self.ki_box.setObjectName(u"ki_box")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.ki_box)

        self.kd_label = QLabel(self.verticalLayoutWidget_2)
        self.kd_label.setObjectName(u"kd_label")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.kd_label)

        self.kd_box = QDoubleSpinBox(self.verticalLayoutWidget_2)
        self.kd_box.setObjectName(u"kd_box")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.kd_box)

        self.i_limit_label = QLabel(self.verticalLayoutWidget_2)
        self.i_limit_label.setObjectName(u"i_limit_label")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.i_limit_label)

        self.i_limit_val_box = QDoubleSpinBox(self.verticalLayoutWidget_2)
        self.i_limit_val_box.setObjectName(u"i_limit_val_box")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.i_limit_val_box)

        self.o_limit_lable = QLabel(self.verticalLayoutWidget_2)
        self.o_limit_lable.setObjectName(u"o_limit_lable")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.o_limit_lable)

        self.o_limit_val_box = QDoubleSpinBox(self.verticalLayoutWidget_2)
        self.o_limit_val_box.setObjectName(u"o_limit_val_box")

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.o_limit_val_box)


        self.verticalLayout_2.addLayout(self.formLayout)

        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pid_info_load = QPushButton(self.verticalLayoutWidget_2)
        self.pid_info_load.setObjectName(u"pid_info_load")

        self.gridLayout.addWidget(self.pid_info_load, 3, 0, 1, 1)

        self.pid_info_save = QPushButton(self.verticalLayoutWidget_2)
        self.pid_info_save.setObjectName(u"pid_info_save")

        self.gridLayout.addWidget(self.pid_info_save, 3, 1, 1, 1)

        self.pid_info_write = QPushButton(self.verticalLayoutWidget_2)
        self.pid_info_write.setObjectName(u"pid_info_write")

        self.gridLayout.addWidget(self.pid_info_write, 0, 1, 1, 1)

        self.pid_info_read = QPushButton(self.verticalLayoutWidget_2)
        self.pid_info_read.setObjectName(u"pid_info_read")

        self.gridLayout.addWidget(self.pid_info_read, 0, 0, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pid_info_label.setText(QCoreApplication.translate("Form", u"PID controller information", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Form", u"speed loop controller", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Form", u"position loop controller", None))

        self.delta_label.setText(QCoreApplication.translate("Form", u"error:", None))
        self.delta_val_label.setText(QCoreApplication.translate("Form", u"0.00", None))
        self.delta_d_label.setText(QCoreApplication.translate("Form", u"error differential:", None))
        self.delta_d_val_label.setText(QCoreApplication.translate("Form", u"0.00", None))
        self.delta_i_label.setText(QCoreApplication.translate("Form", u"error integral:", None))
        self.delta_i_val_label.setText(QCoreApplication.translate("Form", u"0.00", None))
        self.kp_label.setText(QCoreApplication.translate("Form", u"KP\uff1a", None))
        self.ki_label.setText(QCoreApplication.translate("Form", u"KI\uff1a", None))
        self.kd_label.setText(QCoreApplication.translate("Form", u"KD\uff1a", None))
        self.i_limit_label.setText(QCoreApplication.translate("Form", u"intergral limit:", None))
        self.o_limit_lable.setText(QCoreApplication.translate("Form", u"output limit:", None))
        self.pid_info_load.setText(QCoreApplication.translate("Form", u"load", None))
        self.pid_info_save.setText(QCoreApplication.translate("Form", u"save", None))
        self.pid_info_write.setText(QCoreApplication.translate("Form", u"write", None))
        self.pid_info_read.setText(QCoreApplication.translate("Form", u"read", None))
    # retranslateUi

