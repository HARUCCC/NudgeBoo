from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QFileDialog,
    QLineEdit, QFrame, QSpinBox, QCheckBox, QListWidget, QListWidgetItem,
    QTimeEdit, QDialog, QGroupBox, QComboBox, QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTime
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush
from config import load_config, save_config, append_log, get_today_md_path
import os
import sys
import datetime
import json

if getattr(sys, 'frozen', False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(_BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)
TODO_FILE = os.path.join(DATA_DIR, "todos.json")

STYLE = """
QWidget#panel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a1a2e, stop:1 #16213e);
    border-radius: 12px;
}
QLabel#title {
    color: #e2b75e;
    font-size: 22px;
    font-weight: bold;
}
QLabel#subtitle {
    color: #8892b0;
    font-size: 14px;
}
QTextEdit#input {
    background: #233044;
    color: #ccd6f6;
    border: 1px solid #2d4059;
    border-radius: 10px;
    padding: 12px;
    font-size: 15px;
    selection-background-color: #3a506b;
}
QTextEdit#input:focus {
    border-color: #5a7a9a;
}
QTextEdit#preview {
    background: #1e2d3d;
    color: #a8b2d1;
    border: 1px solid #2a3a4a;
    border-radius: 10px;
    padding: 10px;
    font-size: 14px;
}
QPushButton#save {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #e2b75e, stop:1 #d4a843);
    color: #1a1a2e;
    font-size: 15px;
    font-weight: bold;
    padding: 10px 32px;
    border-radius: 8px;
    border: none;
}
QPushButton#save:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ecc96e, stop:1 #e2b850);
}
QPushButton#toggleOn {
    background: #e06060;
    color: white;
    font-size: 14px;
    font-weight: bold;
    padding: 8px 24px;
    border-radius: 8px;
    border: none;
}
QPushButton#toggleOn:hover { background: #d05050; }
QPushButton#toggleOff {
    background: #5a9e6f;
    color: white;
    font-size: 14px;
    font-weight: bold;
    padding: 8px 24px;
    border-radius: 8px;
    border: none;
}
QPushButton#toggleOff:hover { background: #4a8e5f; }
QPushButton#sameBtn {
    background: #2d4059;
    color: #a8b2d1;
    font-size: 14px;
    padding: 8px 20px;
    border-radius: 8px;
    border: 1px solid #3a506b;
}
QPushButton#sameBtn:hover {
    background: #3a506b;
    color: #ccd6f6;
}
QPushButton#subBtn {
    background: #3a506b;
    color: #a8b2d1;
    font-size: 13px;
    padding: 6px 16px;
    border-radius: 6px;
    border: 1px solid #4a6a8a;
}
QPushButton#subBtn:hover {
    background: #4a6a8a;
    color: #ccd6f6;
}
QFrame#divider {
    background: #2d4059;
    max-height: 1px;
}
QSpinBox {
    background: #233044;
    color: #ccd6f6;
    border: 1px solid #2d4059;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 14px;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 20px;
    background: #2d4059;
}
"""




# ─── Settings Panel ─────────────────────────────────────────────

class SettingsPanel(QDialog):
    settings_saved = pyqtSignal()

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.cfg = cfg
        self.setWindowTitle("NudgeBoo - 设置")
        self.setMinimumWidth(420)
        self.setStyleSheet("""
            QDialog { background: #1a1a2e; }
            QGroupBox {
                color: #ccd6f6; border: 1px solid #2d4059;
                border-radius: 8px; margin-top: 12px; padding-top: 20px; font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #e2b75e;
            }
            QLabel { color: #a8b2d1; font-size: 13px; }
            QTimeEdit, QSpinBox, QLineEdit, QComboBox {
                background: #233044; color: #ccd6f6; border: 1px solid #2d4059;
                border-radius: 6px; padding: 6px 10px; font-size: 14px;
            }
            QTimeEdit:focus, QSpinBox:focus, QLineEdit:focus, QComboBox:focus {
                border-color: #5a7a9a;
            }
            QComboBox QAbstractItemView {
                background: #233044; color: #ccd6f6; selection-background-color: #3a506b;
            }
            QPushButton {
                background: #2d4059; color: #a8b2d1; border: 1px solid #3a506b;
                border-radius: 6px; padding: 8px 16px; font-size: 14px;
            }
            QPushButton:hover { background: #3a506b; color: #ccd6f6; }
            QPushButton#saveBtn { background: #e2b75e; color: #1a1a2e; font-weight: bold; border: none; }
            QPushButton#saveBtn:hover { background: #ecc96e; }
            QPushButton#cancelBtn { background: transparent; border: 1px solid #5a7a9a; }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── Work Mode Group ──
        mode_group = QGroupBox("工作模式")
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setSpacing(10)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["固定上下班", "弹性工作制"])
        self.mode_combo.setCurrentIndex(0 if self.cfg.get("work_mode", "fixed") == "fixed" else 1)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_row.addWidget(self.mode_combo)
        mode_row.addStretch()
        mode_layout.addLayout(mode_row)

        # Fixed mode: start/end time
        self.fixed_widget = QWidget()
        fixed_layout = QHBoxLayout(self.fixed_widget)
        fixed_layout.setContentsMargins(0, 0, 0, 0)
        fixed_layout.addWidget(QLabel("上班:"))
        self.time_start = QTimeEdit()
        self.time_start.setDisplayFormat("HH:mm")
        self.time_start.setTime(QTime.fromString(self.cfg.get("work_start", "09:00"), "HH:mm"))
        fixed_layout.addWidget(self.time_start)
        fixed_layout.addStretch()
        fixed_layout.addWidget(QLabel("下班:"))
        self.time_end = QTimeEdit()
        self.time_end.setDisplayFormat("HH:mm")
        self.time_end.setTime(QTime.fromString(self.cfg.get("work_end", "18:00"), "HH:mm"))
        fixed_layout.addWidget(self.time_end)
        mode_layout.addWidget(self.fixed_widget)

        # Flexible mode: duration
        self.flex_widget = QWidget()
        flex_layout = QHBoxLayout(self.flex_widget)
        flex_layout.setContentsMargins(0, 0, 0, 0)
        flex_layout.addWidget(QLabel("每日总时长(含午休):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(4, 16)
        self.duration_spin.setValue(self.cfg.get("work_duration", 9))
        self.duration_spin.setSuffix(" 小时")
        flex_layout.addWidget(self.duration_spin)
        flex_layout.addStretch()
        mode_layout.addWidget(self.flex_widget)

        self._on_mode_changed(self.mode_combo.currentIndex())
        layout.addWidget(mode_group)

        # ── Lunch Group ──
        lunch_group = QGroupBox("午休时间")
        lunch_layout = QHBoxLayout(lunch_group)
        lunch_layout.setSpacing(12)
        lunch_layout.addWidget(QLabel("开始:"))
        self.lunch_start = QTimeEdit()
        self.lunch_start.setDisplayFormat("HH:mm")
        self.lunch_start.setTime(QTime.fromString(self.cfg.get("lunch_start", "12:00"), "HH:mm"))
        lunch_layout.addWidget(self.lunch_start)
        lunch_layout.addStretch()
        lunch_layout.addWidget(QLabel("结束:"))
        self.lunch_end = QTimeEdit()
        self.lunch_end.setDisplayFormat("HH:mm")
        self.lunch_end.setTime(QTime.fromString(self.cfg.get("lunch_end", "13:30"), "HH:mm"))
        lunch_layout.addWidget(self.lunch_end)
        layout.addWidget(lunch_group)

        # ── Reminder Group ──
        reminder_group = QGroupBox("提醒设置")
        reminder_layout = QHBoxLayout(reminder_group)
        reminder_layout.addWidget(QLabel("提醒间隔:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 480)
        self.interval_spin.setValue(self.cfg.get("reminder_interval_min", 120))
        self.interval_spin.setSuffix(" 分钟")
        reminder_layout.addWidget(self.interval_spin)
        reminder_layout.addStretch()
        layout.addWidget(reminder_group)

        # ── Path Group ──
        path_group = QGroupBox("日志路径")
        path_layout = QHBoxLayout(path_group)
        self.path_edit = QLineEdit(self.cfg.get("log_dir", ""))
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit)
        btn_path = QPushButton("选择...")
        btn_path.clicked.connect(self._choose_path)
        path_layout.addWidget(btn_path)
        layout.addWidget(path_group)

        # ── Buttons ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_cancel = QPushButton("取消")
        btn_cancel.setObjectName("cancelBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_save = QPushButton("保存")
        btn_save.setObjectName("saveBtn")
        btn_save.clicked.connect(self._save)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def _on_mode_changed(self, index):
        is_fixed = index == 0
        self.fixed_widget.setVisible(is_fixed)
        self.flex_widget.setVisible(not is_fixed)

    def _choose_path(self):
        d = QFileDialog.getExistingDirectory(self, "选择日志保存目录", self.path_edit.text())
        if d:
            self.path_edit.setText(d)

    def _save(self):
        self.cfg["work_mode"] = "fixed" if self.mode_combo.currentIndex() == 0 else "flexible"
        self.cfg["work_start"] = self.time_start.time().toString("HH:mm")
        self.cfg["work_end"] = self.time_end.time().toString("HH:mm")
        self.cfg["work_duration"] = self.duration_spin.value()
        self.cfg["lunch_start"] = self.lunch_start.time().toString("HH:mm")
        self.cfg["lunch_end"] = self.lunch_end.time().toString("HH:mm")
        self.cfg["reminder_interval_min"] = self.interval_spin.value()
        self.cfg["log_dir"] = self.path_edit.text()
        save_config(self.cfg)
        self.settings_saved.emit()
        self.accept()


# ─── Todo Item ─────────────────────────────────────────────

class TodoItem(QWidget):
    completed = pyqtSignal(str, bool)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self._completed = False
        self.setMinimumHeight(36)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        self.checkbox = QCheckBox()
        self.checkbox.setCursor(Qt.PointingHandCursor)
        self.checkbox.stateChanged.connect(self._on_toggled)
        layout.addWidget(self.checkbox)

        self.label = QLabel(self.text)
        self.label.setStyleSheet("color: #ccd6f6; font-size: 14px; padding: 2px 0;")
        self.label.setWordWrap(True)
        self.label.setCursor(Qt.PointingHandCursor)
        self.label.mousePressEvent = lambda e: self.checkbox.toggle()
        layout.addWidget(self.label, 1)

    def _on_toggled(self, state):
        self._completed = state == Qt.Checked
        if self._completed:
            self.label.setStyleSheet("color: #5a7a9a; font-size: 14px; text-decoration: line-through;")
        else:
            self.label.setStyleSheet("color: #ccd6f6; font-size: 14px;")
        self.completed.emit(self.text, self._completed)

    def is_completed(self):
        return self._completed


# ─── Todo List ─────────────────────────────────────────────

class TodoList(QWidget):
    todo_completed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.todos = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        self.input = QLineEdit()
        self.input.setPlaceholderText("添加待办事项...")
        self.input.setStyleSheet("""
            QLineEdit { background: #233044; color: #ccd6f6; border: 1px solid #2d4059;
                        border-radius: 8px; padding: 8px 12px; font-size: 14px; }
            QLineEdit:focus { border-color: #5a7a9a; }
        """)
        self.input.returnPressed.connect(self._add_todo)
        input_row.addWidget(self.input)

        btn_add = QPushButton("添加")
        btn_add.setStyleSheet("""
            QPushButton { background: #2d4059; color: #a8b2d1; font-size: 14px;
                          padding: 8px 16px; border-radius: 8px; border: 1px solid #3a506b; }
            QPushButton:hover { background: #3a506b; color: #ccd6f6; }
        """)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._add_todo)
        input_row.addWidget(btn_add)
        layout.addLayout(input_row)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { background: #1e2d3d; border: 1px solid #2a3a4a; border-radius: 8px; padding: 4px; }
            QListWidget::item { padding: 4px 2px; }
        """)
        self.list_widget.setMinimumHeight(100)
        layout.addWidget(self.list_widget, 1)

        self._load_todos()

    def _load_todos(self):
        if not os.path.exists(TODO_FILE):
            return
        try:
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                for text in json.load(f):
                    self._add_item(text)
        except:
            pass

    def _save_todos(self):
        try:
            with open(TODO_FILE, "w", encoding="utf-8") as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _add_todo(self):
        text = self.input.text().strip()
        if not text:
            return
        self._add_item(text)
        self.input.clear()
        self._save_todos()

    def _add_item(self, text):
        from PyQt5.QtCore import QSize
        item_widget = TodoItem(text)
        item_widget.completed.connect(self._on_completed)
        list_item = QListWidgetItem()
        hint = item_widget.sizeHint()
        list_item.setSizeHint(QSize(hint.width(), max(hint.height(), 36)))
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, item_widget)
        self.todos.append(text)

    def _on_completed(self, text, is_completed):
        if is_completed:
            self.todo_completed.emit(text)
            if text in self.todos:
                self.todos.remove(text)
                self._save_todos()


# ─── Timeline Bar (Progress) ─────────────────────────────

class TimelineBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0
        self.time_range = None
        self.entry_times = []  # list of (position%, time_str, is_overtime)
        self.overtime = 0
        self._hover_x = -1
        self.setMouseTracking(True)
        self.setMinimumHeight(70)
        self.setMaximumHeight(70)

    def set_progress(self, progress, time_range=None, entry_times=None, overtime=0, normal_ratio=100):
        self.progress = progress or 0
        self.time_range = time_range
        self.entry_times = entry_times or []
        self.overtime = overtime or 0
        self.normal_ratio = normal_ratio or 100
        self.update()

    def mouseMoveEvent(self, event):
        self._hover_x = event.x()
        self.update()

    def leaveEvent(self, event):
        self._hover_x = -1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin = 10
        bar_y = 20
        bar_h = 14
        bar_w = w - margin * 2

        # Background bar
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(30, 45, 61)))
        p.drawRoundedRect(margin, bar_y, bar_w, bar_h, 7, 7)

        # Normal area width = normal_ratio% of total bar
        normal_area_w = int(bar_w * self.normal_ratio / 100)

        # Normal progress fill (gold) - fills within the normal area
        normal_fill_w = int(normal_area_w * min(self.progress, 100) / 100)
        if normal_fill_w > 0:
            p.setBrush(QBrush(QColor(226, 183, 94)))
            p.drawRoundedRect(margin, bar_y, normal_fill_w, bar_h, 7, 7)

        # Overtime fill (red-orange) - starts after normal area
        if self.overtime > 0:
            ot_fill_w = bar_w - normal_area_w
            p.setBrush(QBrush(QColor(220, 80, 60)))
            p.drawRoundedRect(margin + normal_area_w, bar_y, ot_fill_w, bar_h, 7, 7)
            # "加班" label inside the red area
            p.setPen(QColor(255, 220, 200))
            p.setFont(QFont("Microsoft YaHei", 7, QFont.Bold))
            p.drawText(margin + normal_area_w + 4, bar_y, ot_fill_w - 4, bar_h, Qt.AlignCenter, "加班")

        # Find the marker closest to hover
        closest_idx = -1
        closest_dist = 999
        for idx, (pos, time_str, is_ot) in enumerate(self.entry_times):
            x = margin + int(bar_w * pos / 100)
            dist = abs(x - self._hover_x)
            if dist < closest_dist and dist < 20:
                closest_dist = dist
                closest_idx = idx

        # Draw all dots
        for idx, (pos, time_str, is_ot) in enumerate(self.entry_times):
            x = margin + int(bar_w * pos / 100)
            if is_ot:
                p.setBrush(QBrush(QColor(255, 120, 100)))
                p.setPen(Qt.NoPen)
            else:
                p.setBrush(QBrush(QColor(255, 255, 255)))
                p.setPen(Qt.NoPen)
            p.drawEllipse(x - 4, bar_y + bar_h // 2 - 4, 8, 8)

        # Show time label only for the hovered marker
        if closest_idx >= 0:
            pos, time_str, is_ot = self.entry_times[closest_idx]
            x = margin + int(bar_w * pos / 100)
            # Tooltip-style label above
            p.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
            label_color = QColor(255, 150, 130) if is_ot else QColor(226, 183, 94)
            p.setPen(label_color)
            # Background pill for readability
            fm = p.fontMetrics()
            tw = fm.horizontalAdvance(time_str) + 12
            lx = x - tw // 2
            ly = 0
            p.setBrush(QBrush(QColor(26, 26, 46, 220)))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(lx, ly, tw, 18, 9, 9)
            p.setPen(label_color)
            p.drawText(lx, ly, tw, 18, Qt.AlignCenter, time_str)
            # Connecting line
            p.setPen(QPen(QColor(100, 110, 140, 150), 1, Qt.DotLine))
            p.drawLine(x, 18, x, bar_y)

        # Start/end time labels
        if self.time_range:
            start, end = self.time_range
            p.setPen(QColor(80, 90, 120))
            p.setFont(QFont("Microsoft YaHei", 8))
            p.drawText(margin, bar_y + bar_h + 6, 50, 16, Qt.AlignLeft, start.strftime("%H:%M"))
            p.drawText(w - margin - 50, bar_y + bar_h + 6, 50, 16, Qt.AlignRight, end.strftime("%H:%M"))

        p.end()


# ─── Log Panel ─────────────────────────────────────────────

class LogPanel(QWidget):
    log_saved = pyqtSignal()
    recording_toggled = pyqtSignal(bool)
    dnd_toggled = pyqtSignal(bool)

    def __init__(self, timeline=None, parent=None):
        super().__init__(parent)
        self.cfg = load_config()
        self._timeline = timeline
        self._is_recording = timeline.recording if timeline else False
        self._is_dnd = self.cfg.get("dnd_mode", False)
        self.setWindowTitle("NudgeBoo - 写日志！")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.resize(780, 560)
        self.setStyleSheet(STYLE)
        self._setup_ui()
        self._refresh_preview()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        panel = QWidget()
        panel.setObjectName("panel")
        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(24, 20, 24, 16)
        main_layout.setSpacing(10)

        # ── Header ──
        header = QHBoxLayout()
        header.setSpacing(12)

        title = QLabel("写日志！")
        title.setObjectName("title")
        header.addWidget(title)

        subtitle = QLabel(datetime.datetime.now().strftime("%Y/%m/%d"))
        subtitle.setObjectName("subtitle")
        header.addWidget(subtitle)
        header.addStretch()

        self.btn_dnd = QPushButton("🔕 免打扰")
        self.btn_dnd.setStyleSheet("""
            QPushButton { background: transparent; color: #5a7a9a; font-size: 13px;
                          padding: 6px 12px; border: 1px solid #2d4059; border-radius: 6px; }
            QPushButton:hover { color: #8ab4f8; border-color: #5a7a9a; }
        """)
        self.btn_dnd.setCursor(Qt.PointingHandCursor)
        self.btn_dnd.clicked.connect(self._toggle_dnd)
        self._sync_dnd_ui()
        header.addWidget(self.btn_dnd)

        btn_settings = QPushButton("⚙ 设置")
        btn_settings.setStyleSheet("""
            QPushButton { background: transparent; color: #5a7a9a; font-size: 13px;
                          padding: 6px 12px; border: 1px solid #2d4059; border-radius: 6px; }
            QPushButton:hover { color: #8ab4f8; border-color: #5a7a9a; }
        """)
        btn_settings.setCursor(Qt.PointingHandCursor)
        btn_settings.clicked.connect(self._show_settings)
        header.addWidget(btn_settings)

        self.btn_toggle = QPushButton("开始记录")
        self.btn_toggle.setObjectName("toggleOff")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.clicked.connect(self._on_toggle)
        header.addWidget(self.btn_toggle)

        main_layout.addLayout(header)
        main_layout.addWidget(self._divider())

        # ── Content ──
        content = QHBoxLayout()
        content.setSpacing(16)

        # LEFT
        left = QVBoxLayout()
        left.setSpacing(10)

        tl_label = QLabel("时间轴")
        tl_label.setStyleSheet("color: #bbb; font-size: 13px;")
        left.addWidget(tl_label)
        self.timeline_bar = TimelineBar()
        left.addWidget(self.timeline_bar)

        # Input area with text_edit only
        input_label = QLabel("记录内容")
        input_label.setStyleSheet("color: #bbb; font-size: 13px;")
        left.addWidget(input_label)

        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("input")
        self.text_edit.setPlaceholderText("写点什么吧...")
        self.text_edit.setMinimumHeight(100)
        left.addWidget(self.text_edit)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_save = QPushButton("保存记录")
        btn_save.setObjectName("save")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self._save_log)
        btn_row.addWidget(btn_save)

        btn_same = QPushButton("与上段相同")
        btn_same.setObjectName("sameBtn")
        btn_same.setCursor(Qt.PointingHandCursor)
        btn_same.clicked.connect(self._same_as_last)
        btn_row.addWidget(btn_same)

        left.addLayout(btn_row)

        preview_label = QLabel("今日记录")
        preview_label.setStyleSheet("color: #bbb; font-size: 13px;")
        left.addWidget(preview_label)

        self.preview_edit = QTextEdit()
        self.preview_edit.setObjectName("preview")
        self.preview_edit.mouseDoubleClickEvent = self._on_preview_double_click
        self.preview_edit.textChanged.connect(self._on_preview_changed)
        left.addWidget(self.preview_edit)

        self._preview_loading = False  # Flag to prevent sync during load

        # Sub-block markers
        self._SUB_START = "── 子行: {} ──"
        self._SUB_END = "── 结束子行 ──"

        content.addLayout(left, 3)

        # RIGHT: todo
        right = QVBoxLayout()
        right.setSpacing(8)

        todo_label = QLabel("待办事项")
        todo_label.setStyleSheet("color: #e2b75e; font-size: 14px; font-weight: bold;")
        right.addWidget(todo_label)

        self.todo_list = TodoList()
        self.todo_list.todo_completed.connect(self._on_todo_completed)
        right.addWidget(self.todo_list, 1)

        content.addLayout(right, 2)

        main_layout.addLayout(content, 1)
        root.addWidget(panel)

    def _divider(self):
        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.HLine)
        return div

    # ── DND ──

    def _toggle_dnd(self):
        if not self._is_dnd:
            reply = QMessageBox.question(
                self, "免打扰模式",
                "开启后将不会弹出记录提示，幽灵和日志面板都会最小化。\n确定开启吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        self._is_dnd = not self._is_dnd
        self.cfg["dnd_mode"] = self._is_dnd
        save_config(self.cfg)
        self._sync_dnd_ui()
        self.dnd_toggled.emit(self._is_dnd)
        if self._is_dnd:
            self.hide()

    def _sync_dnd_ui(self):
        if self._is_dnd:
            self.btn_dnd.setText("🔔 取消免打扰")
            self.btn_dnd.setStyleSheet("""
                QPushButton { background: #e06060; color: white; font-size: 13px;
                              padding: 6px 12px; border: none; border-radius: 6px; }
                QPushButton:hover { background: #d05050; }
            """)
        else:
            self.btn_dnd.setText("🔕 免打扰")
            self.btn_dnd.setStyleSheet("""
                QPushButton { background: transparent; color: #5a7a9a; font-size: 13px;
                              padding: 6px 12px; border: 1px solid #2d4059; border-radius: 6px; }
                QPushButton:hover { color: #8ab4f8; border-color: #5a7a9a; }
            """)

    # ── Toggle recording ──

    def _on_toggle(self):
        self._is_recording = not self._is_recording
        self._sync_toggle_ui()
        self.recording_toggled.emit(self._is_recording)

    def _sync_toggle_ui(self):
        if self._is_recording:
            self.btn_toggle.setText("停止记录")
            self.btn_toggle.setObjectName("toggleOn")
        else:
            self.btn_toggle.setText("开始记录")
            self.btn_toggle.setObjectName("toggleOff")
        self.style().unpolish(self.btn_toggle)
        self.style().polish(self.btn_toggle)

    def update_toggle(self, is_on):
        self._is_recording = is_on
        self._sync_toggle_ui()

    # ── Settings ──

    def _show_settings(self):
        dialog = SettingsPanel(self.cfg.copy(), self)
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec_()

    def _on_settings_saved(self):
        self.cfg = load_config()
        self._refresh_preview()
        self.update_timeline()

    # ── Log ──

    def _save_log(self):
        if not self._is_recording:
            QMessageBox.information(self, "提示", "请先点击「开始记录」再保存内容")
            return

        raw = self.text_edit.toPlainText()
        now = datetime.datetime.now().strftime("%H:%M")

        # Parse text_edit: extract sub-blocks and new content
        sub_blocks, new_lines = self._parse_editor_content(raw)

        # Save sub-blocks: replace sub-lines in file
        for parent, sub_lines in sub_blocks:
            self._replace_sub_lines_in_file(parent, sub_lines, now)
            # Each sub-line is an independent record with its own timestamp
            for sl in sub_lines:
                if self._timeline:
                    self._timeline.record_entry(sl)

        # Save new content
        for line in new_lines:
            append_log(self.cfg, f"{line} [{now}]")
            if self._timeline:
                self._timeline.record_entry(line)

        self.text_edit.clear()
        self._refresh_preview()
        self.update_timeline()
        self.log_saved.emit()

    def _delete_line_from_file(self, line_text):
        """Delete a specific line from the log file."""
        path = get_today_md_path(self.cfg)
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = [l for l in lines if line_text not in l]
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    def _replace_line_in_file(self, old_line, new_content):
        """Replace a line's content, update timestamp."""
        path = get_today_md_path(self.cfg)
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        now = datetime.datetime.now().strftime("%H:%M")
        new_lines = []
        for line in lines:
            if old_line in line:
                indent = "\t" if line.startswith("\t") else ""
                new_lines.append(f"{indent}{new_content} [{now}]\n")
            else:
                new_lines.append(line)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    def _parse_editor_content(self, raw):
        """Parse editor text into (sub_blocks, new_lines).
        sub_blocks: list of (parent_text, [sub_line_texts])
        new_lines: list of plain text lines
        """
        sub_blocks = []
        new_lines = []
        lines = raw.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]
            # Check for sub-block start marker
            if line.startswith("── 子行:") and line.endswith("──"):
                # Extract parent text
                parent = line[len("── 子行:"):].rstrip("──").strip()
                i += 1
                sub_lines = []
                while i < len(lines):
                    if lines[i].strip() == "── 结束子行 ──":
                        i += 1
                        break
                    if lines[i].strip():
                        sub_lines.append(lines[i].strip())
                    i += 1
                sub_blocks.append((parent, sub_lines))
            else:
                stripped = line.strip()
                if stripped:
                    new_lines.append(stripped)
                i += 1

        return sub_blocks, new_lines

    def _replace_sub_lines_in_file(self, parent, sub_lines, now):
        """Add new sub-lines under a parent, keeping existing ones."""
        path = get_today_md_path(self.cfg)
        if not os.path.exists(path):
            return

        with open(path, "r", encoding="utf-8") as f:
            file_lines = f.readlines()

        # Find existing sub-lines for this parent
        existing_contents = set()
        found_parent = False
        for line in file_lines:
            if not found_parent:
                if parent in line and not line.startswith("\t"):
                    found_parent = True
                continue
            if line.startswith("\t"):
                # Extract content after timestamp like [HH:MM]
                content = line.strip()
                if content.startswith("[") and "]" in content:
                    content = content[content.index("]") + 1:].strip()
                existing_contents.add(content)
            else:
                break

        # Only add sub-lines that don't already exist
        new_sub_lines = []
        for sl in sub_lines:
            if sl.strip() and sl.strip() not in existing_contents:
                new_sub_lines.append(f"\t{sl.strip()} [{now}]\n")

        if not new_sub_lines:
            return

        # Insert new sub-lines after existing ones
        new_file_lines = []
        i = 0
        while i < len(file_lines):
            line = file_lines[i]
            new_file_lines.append(line)
            if parent in line and not line.startswith("\t"):
                i += 1
                # Copy existing sub-lines
                while i < len(file_lines) and file_lines[i].startswith("\t"):
                    new_file_lines.append(file_lines[i])
                    i += 1
                # Append new sub-lines
                for sl in new_sub_lines:
                    new_file_lines.append(sl)
            else:
                i += 1

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_file_lines)

    def _same_as_last(self):
        if not self._is_recording:
            QMessageBox.information(self, "提示", "请先点击「开始记录」再保存内容")
            return
        if not self._timeline or not self._timeline.entries_today:
            return
        # Only add a timeline node and update ghost state, no text update
        self._timeline.record_entry("")
        self.update_timeline()
        self.log_saved.emit()

    def _on_preview_double_click(self, event):
        """Double click: insert sub-block for the clicked md line."""
        if not self._is_recording:
            QTextEdit.mouseDoubleClickEvent(self.preview_edit, event)
            return

        # Use block() to get the actual file line, not the visual wrapped line
        cursor = self.preview_edit.cursorForPosition(event.pos())
        line_text = cursor.block().text().strip()

        parent = None
        if line_text and not line_text.startswith("暂无记录"):
            if line_text.startswith("\t"):
                parent = self._find_parent_of_sub(line_text)
            else:
                parent = line_text

        if parent:
            full_text = self.text_edit.toPlainText()
            marker = self._SUB_START.format(parent)
            if marker in full_text:
                return

            sub_lines = self._get_sub_lines(parent)
            sub_text = ""
            for sl in sub_lines:
                sl = sl.strip().lstrip("\t")
                if sl:
                    sub_text += sl + "\n"

            block = f"\n{marker}\n{sub_text}\n{self._SUB_END}\n"
            tc = self.text_edit.textCursor()
            tc.movePosition(tc.End)
            tc.insertText(block)
            self.text_edit.setTextCursor(tc)
            cursor = self.text_edit.textCursor()
            cursor.movePosition(cursor.Start)
            self.text_edit.setTextCursor(cursor)
            if self.text_edit.find(marker):
                cursor = self.text_edit.textCursor()
                cursor.movePosition(cursor.Down)
                self.text_edit.setTextCursor(cursor)

        QTextEdit.mouseDoubleClickEvent(self.preview_edit, event)

    def _on_preview_right_click(self, pos):
        pass  # Default context menu

    def _get_sub_lines(self, parent_text):
        path = get_today_md_path(self.cfg)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        result = []
        found = False
        for line in lines:
            if not found:
                if parent_text in line and not line.startswith("\t"):
                    found = True
                continue
            if line.startswith("\t"):
                result.append(line)
            else:
                break
        return result

    def _find_parent_of_sub(self, sub_text):
        path = get_today_md_path(self.cfg)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        last_parent = None
        for line in lines:
            if not line.startswith("\t") and line.strip():
                last_parent = line.strip()
            if sub_text in line:
                return last_parent
        return None

    def _on_todo_completed(self, text):
        now = datetime.datetime.now().strftime("%H:%M")
        log_entry = f"[{now}] ✅ 完成待办: {text}"
        append_log(self.cfg, log_entry)
        if self._timeline:
            self._timeline.record_entry(log_entry)
        self._refresh_preview()
        self.log_saved.emit()

    # ── Preview & Timeline ──

    def _on_preview_changed(self):
        """Auto-sync preview content to md file (no timeline entry)."""
        if self._preview_loading:
            return
        path = get_today_md_path(self.cfg)
        content = self.preview_edit.toPlainText()
        if content.strip() == "暂无记录":
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _refresh_preview(self):
        if self.preview_edit.hasFocus():
            return
        self._preview_loading = True
        path = get_today_md_path(self.cfg)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.preview_edit.setPlainText(f.read())
        else:
            self.preview_edit.setPlainText("暂无记录")
        self._preview_loading = False

    def update_timeline(self):
        if self._timeline:
            progress, time_range, entry_times, overtime, normal_ratio = self._timeline.get_progress_info(self.cfg)
            self.timeline_bar.set_progress(progress, time_range, entry_times, overtime, normal_ratio)

    def showEvent(self, event):
        super().showEvent(event)
        self.cfg = load_config()
        self._is_dnd = self.cfg.get("dnd_mode", False)
        self._sync_dnd_ui()
        self._refresh_preview()
        self.update_timeline()
        self._sync_toggle_ui()
