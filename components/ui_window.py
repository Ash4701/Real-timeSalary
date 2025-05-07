# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    QPoint,
    QEvent,
    QRect,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtGui import QCursor, QPainter, QBrush, QColor, QLinearGradient


class AutoHideWindow(QWidget):
    def __init__(
        self,
        margin=5,
        snap_threshold=20,
        animation_duration=250,
        hide_delay=500,
    ):
        super().__init__()

        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.installEventFilter(self)

        self.auto_hide_margin = margin
        self.snap_threshold = snap_threshold
        self.animation_duration = animation_duration
        self.hide_delay = hide_delay

        self.dragging = False
        self.drag_position = QPoint()
        self.hidden_edge = None
        self._is_hidden = False
        self._is_animating = False

        self.screen_geometry = QApplication.primaryScreen().availableGeometry()

        # 总体布局（缩小边距为 8）
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(8, 8, 8, 8)
        self._main_layout.setSpacing(0)

        # 标题栏布局：左右分栏
        self._title_bar_layout = QHBoxLayout()
        self._title_bar_layout.setContentsMargins(0, 0, 0, 0)
        self._title_bar_layout.setSpacing(6)

        self._left_buttons_layout = QHBoxLayout()
        self._left_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._left_buttons_layout.setSpacing(4)

        self._right_buttons_layout = QHBoxLayout()
        self._right_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._right_buttons_layout.setSpacing(4)

        self._title_bar_layout.addLayout(self._left_buttons_layout)
        self._title_bar_layout.addStretch()
        self._title_bar_layout.addLayout(self._right_buttons_layout)

        self._main_layout.addLayout(self._title_bar_layout)

        # 主内容区域
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 6, 0, 0)
        self._main_layout.addLayout(self._content_layout)

        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.check_mouse_position)
        self.monitor_timer.start(200)

        self.leave_timer = QTimer(self)
        self.leave_timer.setSingleShot(True)
        self.leave_timer.timeout.connect(self.auto_hide_window)

    # ---------- 公共接口 ----------
    def addWidget(self, widget):
        self._content_layout.addWidget(widget)

    def addLayout(self, layout):
        self._content_layout.addLayout(layout)

    def addTitleBarLeftWidget(self, widget):
        self._left_buttons_layout.addWidget(widget)

    def addTitleBarRightWidget(self, widget):
        self._right_buttons_layout.addWidget(widget)

    # ---------- 拖动 ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self.snap_to_edges()

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def snap_to_edges(self):
        pos = self.pos()
        screen = self.screen_geometry
        new_x, new_y = pos.x(), pos.y()

        if abs(pos.x()) < self.snap_threshold:
            new_x = 0
        if abs((pos.x() + self.width()) - screen.width()) < self.snap_threshold:
            new_x = screen.width() - self.width()
        if abs(pos.y()) < self.snap_threshold:
            new_y = 0

        self.move(new_x, new_y)

    # ---------- 自动隐藏 ----------
    def moveEvent(self, event):
        self.update_hidden_edge()

    def update_hidden_edge(self):
        pos = self.pos()
        screen = self.screen_geometry

        if pos.x() <= 0:
            self.hidden_edge = "left"
        elif pos.x() + self.width() >= screen.width():
            self.hidden_edge = "right"
        elif pos.y() <= 0:
            self.hidden_edge = "top"
        else:
            self.hidden_edge = None

    def auto_hide_window(self):
        if not self.hidden_edge or self._is_hidden or self._is_animating:
            return

        start_rect = self.geometry()
        end_rect = QRect(start_rect)

        if self.hidden_edge == "left":
            end_rect.moveLeft(1 - self.width() + self.auto_hide_margin)
        elif self.hidden_edge == "right":
            end_rect.moveLeft(self.screen_geometry.width() - self.auto_hide_margin)
        elif self.hidden_edge == "top":
            end_rect.moveTop(1 - self.height() + self.auto_hide_margin)

        self.animate_geometry(start_rect, end_rect)
        self._is_hidden = True

    def show_full_window(self):
        if not self.hidden_edge or not self._is_hidden or self._is_animating:
            return

        start_rect = self.geometry()
        end_rect = QRect(start_rect)

        if self.hidden_edge == "left":
            end_rect.moveLeft(0)
        elif self.hidden_edge == "right":
            end_rect.moveLeft(self.screen_geometry.width() - self.width())
        elif self.hidden_edge == "top":
            end_rect.moveTop(0)

        self.animate_geometry(start_rect, end_rect)
        self._is_hidden = False

    def animate_geometry(self, start_rect, end_rect):
        if start_rect == end_rect:
            return
        self._is_animating = True
        self.anim = QPropertyAnimation(self, b"geometry", self)
        self.anim.setDuration(self.animation_duration)
        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(end_rect)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.finished.connect(self.on_animation_finished)
        self.anim.start()

    def on_animation_finished(self):
        self._is_animating = False

    def check_mouse_position(self):
        if not self.hidden_edge or not self._is_hidden or self._is_animating:
            return

        cursor = QCursor.pos()
        screen = self.screen_geometry

        if self.hidden_edge == "left" and cursor.x() <= self.auto_hide_margin:
            self.show_full_window()
        elif (
            self.hidden_edge == "right"
            and cursor.x() >= screen.width() - self.auto_hide_margin
        ):
            self.show_full_window()
        elif self.hidden_edge == "top" and cursor.y() <= self.auto_hide_margin:
            self.show_full_window()

    def enterEvent(self, event):
        self.leave_timer.stop()

    def leaveEvent(self, event):
        if self.hidden_edge and not self._is_hidden:
            self.leave_timer.start(self.hide_delay)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            self.leave_timer.stop()
        elif event.type() == QEvent.Leave:
            if self.hidden_edge and not self._is_hidden:
                self.leave_timer.start(self.hide_delay)
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 创建渐变背景
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#eaf0ff"))
        gradient.setColorAt(1, QColor("#f6faff"))

        # 设置渐变作为背景填充
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)

        # 绘制带圆角的矩形
        painter.drawRoundedRect(self.rect(), 8, 8)  # 圆角半径为20px
        painter.end()
