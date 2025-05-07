# -*- coding: utf-8 -*-
import sys
from PySide6.QtWidgets import QApplication, QLabel, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction, QGuiApplication
from components.ui_button import FluentCloseButton
from components.ui_widget import SalaryCalculatorWidget
from components.ui_window import AutoHideWindow
from resources import resource

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建窗口
    window = AutoHideWindow()
    window.resize(320, 220)
    window.addWidget(SalaryCalculatorWidget())

    # 创建关闭按钮，绑定 window 关闭
    close_btn = FluentCloseButton(target_window=window)
    window.addTitleBarRightWidget(close_btn)

    # 创建托盘图标
    tray_icon = QSystemTrayIcon(QIcon(":/app/icon.png"), parent=app)
    tray_icon.setToolTip("Salary Calculator")

    # 创建托盘右键菜单
    tray_menu = QMenu()
    quit_action = QAction("退出", app)
    quit_action.triggered.connect(app.quit)

    tray_menu.addAction(quit_action)
    # 设置 QMenu 样式，调整字体
    tray_menu.setStyleSheet("""
        QMenu {
            font-size: 12px;
        }
        QMenu::item {
            color: #333333;
            padding: 5px 20px;
        }
        QMenu::item:selected {
            background-color: #eaf0ff;
            border-radius: 8px;
        }
    """)
    tray_icon.setContextMenu(tray_menu)

    # 点击托盘图标时的处理
    def on_tray_icon_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # 单击托盘图标
            if window.isVisible():
                window.hide()  # 如果窗口已经可见，则隐藏它
            else:
                window.show()  # 如果窗口不可见，则显示它

    # 绑定托盘图标的点击事件
    tray_icon.activated.connect(on_tray_icon_activated)

    # 显示托盘图标
    tray_icon.show()

    # 设置窗口不显示在任务栏
    window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

    # 获取主屏幕的尺寸，计算右下角位置
    screen = QGuiApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()

    # 设置距离右侧和底部的固定距离（单位：像素）
    margin_right = 10  # 距离右侧的距离
    margin_bottom = 80  # 距离底部的距离

    # 计算窗口的位置
    x = (
        screen_geometry.right() - window.width() - margin_right
    )  # 右边缘 - 窗口宽度 - 固定距离
    y = (
        screen_geometry.bottom() - window.height() - margin_bottom
    )  # 底边缘 - 窗口高度 - 固定距离
    window.move(x, y)  # 设置窗口位置

    # 初始时显示窗口
    window.show()

    # 退出应用时销毁托盘图标
    sys.exit(app.exec())
