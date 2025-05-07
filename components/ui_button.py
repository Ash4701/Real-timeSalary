# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QPushButton,
)
from PySide6.QtCore import (
    QSize,
)


class FluentCloseButton(QPushButton):
    def __init__(self, target_window=None, on_click=None, parent=None):
        super().__init__("✕", parent)
        self.setFixedSize(QSize(28, 28))
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: black;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #E81123;
                color: white;
                border-radius: 4px;
            }
        """)

        self._target_window = target_window
        self._on_click = on_click

        self.clicked.connect(self.handle_click)

    def handle_click(self):
        if self._on_click:
            self._on_click()
        elif self._target_window:
            self._target_window.hide()
