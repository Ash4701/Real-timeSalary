# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget,
    QStackedWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTimeEdit,
    QFrame,
)
from PySide6.QtCore import QTimer, QTime, QSettings


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(16)

        self.setStyleSheet("""
            QLineEdit, QTimeEdit {
                background: white;
                border: none;
                padding: 8px;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7286D3, stop:1 #8EA7E9);
                color: white;
                border: none;
                padding: 8px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6a7ed0, stop:1 #839fdf);
            }
            QLabel {
                font-size: 16px;
            }
            QTimeEdit::down-button, QTimeEdit::up-button {
                width: 0px;
                height: 0px;
                border: none;
                background: transparent;
            }
        """)

        # Input fields
        self.salary_input = QLineEdit()
        self.salary_input.setPlaceholderText("月工资 (¥)")

        self.days_input = QLineEdit()
        self.days_input.setPlaceholderText("每月工作天数")

        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat("HH:mm")
        self.start_time.setTime(QTime(8, 30))

        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat("HH:mm")
        self.end_time.setTime(QTime(17, 30))

        self.save_btn = QPushButton("💾 保存并开始计算")

        # Layout setup
        layout.addWidget(QLabel("💰 月工资 (¥)"), 0, 0)
        layout.addWidget(self.salary_input, 1, 0)

        layout.addWidget(QLabel("📅 每月工作天数"), 0, 1)
        layout.addWidget(self.days_input, 1, 1)

        layout.addWidget(QLabel("⏰ 上班时间"), 2, 0)
        layout.addWidget(self.start_time, 3, 0)

        layout.addWidget(QLabel("🕔 下班时间"), 2, 1)
        layout.addWidget(self.end_time, 3, 1)

        # Save button
        layout.addWidget(self.save_btn, 4, 0, 1, 2)  # Span across two columns

        # Set the layout for the window
        self.setLayout(layout)


class ResultPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(16)

        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
            }
            #timeLabel {
                font-size: 14px;
                color: #555;
            }
            #countdownLabel {
                font-size: 14px;
                color: #444;
            }
            #amountLabel {
                font-size: 32px;
                font-weight: bold;
            }
            #statusLabel {
                color: #888;
            }
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f78ca0, stop:1 #f9748f);
                color: white;
                border: none;
                padding: 8px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        self.countdown_label = QLabel("下班倒计时: --:--:--")
        self.countdown_label.setObjectName("countdownLabel")

        self.status_label = QLabel("工作状态: 未知")
        self.status_label.setObjectName("statusLabel")

        self.amount_label = QLabel("￥0.00")
        self.amount_label.setObjectName("amountLabel")

        self.today_total_label = QLabel("今日总计: ￥0.00")

        self.back_button = QPushButton("🔧 修改设置")

        layout.addWidget(self.countdown_label)
        layout.addWidget(self.status_label)
        layout.addSpacing(8)

        self.progress_bg = QFrame()
        self.progress_bg.setFixedHeight(6)
        self.progress_bg.setStyleSheet("background-color: #c3d5ff; border-radius: 3px;")

        self.progress_bar = QFrame(self.progress_bg)
        self.progress_bar.setStyleSheet(
            "background-color: #7286D3; border-radius: 3px;"
        )
        self.progress_bar.setGeometry(0, 0, 0, 6)
        layout.addWidget(self.progress_bg)

        layout.addSpacing(8)
        layout.addWidget(self.amount_label)
        layout.addWidget(self.today_total_label)
        layout.addStretch()
        layout.addWidget(self.back_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)

        self.work_start = QTime(8, 30)
        self.work_end = QTime(17, 30)
        self.salary = 0
        self.days = 22

    def update_ui(self):
        now = QTime.currentTime()

        seconds_worked = self.seconds_today_worked(now)
        total_seconds = self.work_start.secsTo(self.work_end)
        status = "工作中" if self.work_start <= now <= self.work_end else "下班"
        self.status_label.setText(f"工作状态: {status}")

        # 下班倒计时
        if now < self.work_end:
            secs_left = now.secsTo(self.work_end)
            h = secs_left // 3600
            m = (secs_left % 3600) // 60
            s = secs_left % 60
            self.countdown_label.setText(f"下班倒计时: {h:02d}:{m:02d}:{s:02d}")
        else:
            self.countdown_label.setText("下班倒计时: 00:00:00")

        if total_seconds > 0 and self.days > 0:
            salary_per_sec = self.salary / self.days / total_seconds
            earned = salary_per_sec * seconds_worked
            self.amount_label.setText(f"￥{earned:.2f}")
            self.today_total_label.setText(
                f"今日总计: ￥{salary_per_sec * total_seconds:.2f}"
            )

            # 更新进度条宽度
            progress_ratio = min(seconds_worked / total_seconds, 1.0)
            full_width = self.progress_bg.width()
            self.progress_bar.setFixedWidth(int(full_width * progress_ratio))

    def seconds_today_worked(self, now):
        if now < self.work_start:
            return 0
        elif now > self.work_end:
            return self.work_start.secsTo(self.work_end)
        else:
            return self.work_start.secsTo(now)

    def apply_settings(self, salary, days, start, end):
        self.salary = salary
        self.days = days
        self.work_start = start
        self.work_end = end

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_ui()


class SalaryCalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.pages = QStackedWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.pages)
        layout.setContentsMargins(0, 0, 0, 0)

        self.settings_page = SettingsPage()
        self.result_page = ResultPage()

        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.result_page)

        self.settings_page.save_btn.clicked.connect(self.on_save)
        self.result_page.back_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(0)
        )

        self.settings = QSettings("Real-time Salary", "SalaryApp")  # 可替换为实际名称
        self.try_load_settings()

    def try_load_settings(self):
        if (
            self.settings.contains("salary")
            and self.settings.contains("days")
            and self.settings.contains("start")
            and self.settings.contains("end")
        ):
            salary = float(self.settings.value("salary"))
            days = int(self.settings.value("days"))
            start = QTime.fromString(self.settings.value("start"), "HH:mm")
            end = QTime.fromString(self.settings.value("end"), "HH:mm")

            # 写入设置页（用于展示）
            self.settings_page.salary_input.setText(str(salary))
            self.settings_page.days_input.setText(str(days))
            self.settings_page.start_time.setTime(start)
            self.settings_page.end_time.setTime(end)

            # 应用设置并跳转页面
            self.result_page.apply_settings(salary, days, start, end)
            self.pages.setCurrentIndex(1)
        else:
            self.pages.setCurrentIndex(0)

    def on_save(self):
        salary = float(self.settings_page.salary_input.text())
        days = int(self.settings_page.days_input.text())
        start = self.settings_page.start_time.time()
        end = self.settings_page.end_time.time()

        # 保存配置
        self.settings.setValue("salary", salary)
        self.settings.setValue("days", days)
        self.settings.setValue("start", start.toString("HH:mm"))
        self.settings.setValue("end", end.toString("HH:mm"))

        # 应用设置
        self.result_page.apply_settings(salary, days, start, end)
        self.pages.setCurrentIndex(1)
