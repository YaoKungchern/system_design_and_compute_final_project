# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'control_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QGridLayout,
    QLabel, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(500, 235)
        Form.setMinimumSize(QSize(500, 205))
        self.verticalLayoutWidget = QWidget(Form)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 481, 211))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.control_info_label = QLabel(self.verticalLayoutWidget)
        self.control_info_label.setObjectName(u"control_info_label")
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.control_info_label.setFont(font)

        self.verticalLayout.addWidget(self.control_info_label)

        self.mode_box = QComboBox(self.verticalLayoutWidget)
        self.mode_box.addItem("")
        self.mode_box.addItem("")
        self.mode_box.setObjectName(u"mode_box")

        self.verticalLayout.addWidget(self.mode_box)

        self.control_mode_box = QComboBox(self.verticalLayoutWidget)
        self.control_mode_box.addItem("")
        self.control_mode_box.addItem("")
        self.control_mode_box.addItem("")
        self.control_mode_box.addItem("")
        self.control_mode_box.addItem("")
        self.control_mode_box.setObjectName(u"control_mode_box")

        self.verticalLayout.addWidget(self.control_mode_box)

        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.x_label = QLabel(self.verticalLayoutWidget)
        self.x_label.setObjectName(u"x_label")

        self.gridLayout.addWidget(self.x_label, 0, 0, 1, 1)

        self.y_unit_label = QLabel(self.verticalLayoutWidget)
        self.y_unit_label.setObjectName(u"y_unit_label")

        self.gridLayout.addWidget(self.y_unit_label, 1, 4, 1, 1)

        self.x_box = QDoubleSpinBox(self.verticalLayoutWidget)
        self.x_box.setObjectName(u"x_box")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.x_box.sizePolicy().hasHeightForWidth())
        self.x_box.setSizePolicy(sizePolicy)
        self.x_box.setMinimum(-999.000000000000000)
        self.x_box.setMaximum(999.990000000000009)
        self.x_box.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.x_box, 0, 3, 1, 1)

        self.y_box = QDoubleSpinBox(self.verticalLayoutWidget)
        self.y_box.setObjectName(u"y_box")
        sizePolicy.setHeightForWidth(self.y_box.sizePolicy().hasHeightForWidth())
        self.y_box.setSizePolicy(sizePolicy)
        self.y_box.setMinimum(-999.990000000000009)
        self.y_box.setMaximum(999.990000000000009)

        self.gridLayout.addWidget(self.y_box, 1, 3, 1, 1)

        self.y_label = QLabel(self.verticalLayoutWidget)
        self.y_label.setObjectName(u"y_label")

        self.gridLayout.addWidget(self.y_label, 1, 0, 1, 1)

        self.x_unit_label = QLabel(self.verticalLayoutWidget)
        self.x_unit_label.setObjectName(u"x_unit_label")

        self.gridLayout.addWidget(self.x_unit_label, 0, 4, 1, 1)

        self.yaw_label = QLabel(self.verticalLayoutWidget)
        self.yaw_label.setObjectName(u"yaw_label")

        self.gridLayout.addWidget(self.yaw_label, 2, 0, 1, 1)

        self.yaw_box = QDoubleSpinBox(self.verticalLayoutWidget)
        self.yaw_box.setObjectName(u"yaw_box")
        sizePolicy.setHeightForWidth(self.yaw_box.sizePolicy().hasHeightForWidth())
        self.yaw_box.setSizePolicy(sizePolicy)
        self.yaw_box.setMinimum(-999.990000000000009)
        self.yaw_box.setMaximum(999.990000000000009)

        self.gridLayout.addWidget(self.yaw_box, 2, 3, 1, 1)

        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 2, 4, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.control_set_button = QPushButton(self.verticalLayoutWidget)
        self.control_set_button.setObjectName(u"control_set_button")

        self.verticalLayout.addWidget(self.control_set_button)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.control_info_label.setText(QCoreApplication.translate("Form", u"motion control", None))
        self.mode_box.setItemText(0, QCoreApplication.translate("Form", u"manul mode", None))
        self.mode_box.setItemText(1, QCoreApplication.translate("Form", u"controller mode", None))

        self.control_mode_box.setItemText(0, QCoreApplication.translate("Form", u"openloop control", None))
        self.control_mode_box.setItemText(1, QCoreApplication.translate("Form", u"speed closedloop control under robot base", None))
        self.control_mode_box.setItemText(2, QCoreApplication.translate("Form", u"speed closedloop control under world base", None))
        self.control_mode_box.setItemText(3, QCoreApplication.translate("Form", u"position closedloop control under robot base", None))
        self.control_mode_box.setItemText(4, QCoreApplication.translate("Form", u"position closedloop control under world base", None))

        self.x_label.setText(QCoreApplication.translate("Form", u"X:", None))
        self.y_unit_label.setText(QCoreApplication.translate("Form", u"m/s", None))
        self.y_label.setText(QCoreApplication.translate("Form", u"Y:", None))
        self.x_unit_label.setText(QCoreApplication.translate("Form", u"m/s", None))
        self.yaw_label.setText(QCoreApplication.translate("Form", u"yaw:", None))
        self.label.setText(QCoreApplication.translate("Form", u"deg/s", None))
        self.control_set_button.setText(QCoreApplication.translate("Form", u"write", None))
    # retranslateUi

