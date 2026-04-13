# -*- coding: utf-8 -*-
import sys
from PySide6.QtWidgets import QApplication
from main_func import NewMainWidget

if __name__ == "__main__":
    # 解决PyQtGraph中文显示问题
    import pyqtgraph as pg
    # pg.setConfigOption('font.family', 'SimHei')
    # pg.setConfigOption('font.size', 10)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 设置统一风格

    # 创建主界面
    main_widget = NewMainWidget()
    main_widget.show()

    sys.exit(app.exec())