# -*- coding: utf-8 -*-
import sys
from PySide6.QtWidgets import QApplication
from main_func import NewMainWidget

if __name__ == "__main__":
    import pyqtgraph as pg

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 设置统一风格

    # 创建主界面
    main_widget = NewMainWidget()
    main_widget.show()

    sys.exit(app.exec())
    
'''__||_____||__
   __||_____||__
   ___\\___//___
   _===========_
   _____|||_____
   _____|||_____
   ______|______
   ___防伪专用___'''