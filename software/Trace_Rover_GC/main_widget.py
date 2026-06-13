# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(251, 366)
        Form.setMinimumSize(QSize(251, 366))
        Form.setSizeIncrement(QSize(0, 0))
        Form.setBaseSize(QSize(251, 454))
        self.verticalLayoutWidget_2 = QWidget(Form)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(10, 170, 231, 181))
        self.verticalLayout_1 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_1.setObjectName(u"verticalLayout_1")
        self.verticalLayout_1.setContentsMargins(0, 0, 0, 0)
        self.mod_label = QLabel(self.verticalLayoutWidget_2)
        self.mod_label.setObjectName(u"mod_label")
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.mod_label.setFont(font)

        self.verticalLayout_1.addWidget(self.mod_label)

        self.control_button = QPushButton(self.verticalLayoutWidget_2)
        self.control_button.setObjectName(u"control_button")

        self.verticalLayout_1.addWidget(self.control_button)

        self.vision_button = QPushButton(self.verticalLayoutWidget_2)
        self.vision_button.setObjectName(u"vision_button")

        self.verticalLayout_1.addWidget(self.vision_button)

        self.navigation_button = QPushButton(self.verticalLayoutWidget_2)
        self.navigation_button.setObjectName(u"navigation_button")

        self.verticalLayout_1.addWidget(self.navigation_button)

        self.pid_button = QPushButton(self.verticalLayoutWidget_2)
        self.pid_button.setObjectName(u"pid_button")

        self.verticalLayout_1.addWidget(self.pid_button)

        self.mission_button = QPushButton(self.verticalLayoutWidget_2)
        self.mission_button.setObjectName(u"mission_button")

        self.verticalLayout_1.addWidget(self.mission_button)

        self.verticalLayoutWidget_3 = QWidget(Form)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(10, 10, 231, 145))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.device_label = QLabel(self.verticalLayoutWidget_3)
        self.device_label.setObjectName(u"device_label")
        self.device_label.setFont(font)

        self.verticalLayout_2.addWidget(self.device_label)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.mac_label = QLabel(self.verticalLayoutWidget_3)
        self.mac_label.setObjectName(u"mac_label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.mac_label)

        self.state_label = QLabel(self.verticalLayoutWidget_3)
        self.state_label.setObjectName(u"state_label")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.state_label)

        self.connect_state = QLabel(self.verticalLayoutWidget_3)
        self.connect_state.setObjectName(u"connect_state")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.connect_state)

        self.mac_line = QLineEdit(self.verticalLayoutWidget_3)
        self.mac_line.setObjectName(u"mac_line")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.mac_line)


        self.verticalLayout_2.addLayout(self.formLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.disconnect_button = QPushButton(self.verticalLayoutWidget_3)
        self.disconnect_button.setObjectName(u"disconnect_button")

        self.horizontalLayout_2.addWidget(self.disconnect_button)

        self.connect_button = QPushButton(self.verticalLayoutWidget_3)
        self.connect_button.setObjectName(u"connect_button")

        self.horizontalLayout_2.addWidget(self.connect_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.mod_label.setText(QCoreApplication.translate("Form", u"function module", None))
        self.control_button.setText(QCoreApplication.translate("Form", u"motion controll", None))
        self.vision_button.setText(QCoreApplication.translate("Form", u"video stream", None))
        self.navigation_button.setText(QCoreApplication.translate("Form", u"navigation information", None))
        self.pid_button.setText(QCoreApplication.translate("Form", u"PID parameter tuning", None))
        self.mission_button.setText(QCoreApplication.translate("Form", u"mission planning", None))
        self.device_label.setText(QCoreApplication.translate("Form", u"device management", None))
        self.mac_label.setText(QCoreApplication.translate("Form", u"MAC:", None))
        self.state_label.setText(QCoreApplication.translate("Form", u"connection:", None))
        self.connect_state.setText(QCoreApplication.translate("Form", u"unconnected", None))
        self.disconnect_button.setText(QCoreApplication.translate("Form", u"disconnect", None))
        self.connect_button.setText(QCoreApplication.translate("Form", u"connect", None))
    # retranslateUi

