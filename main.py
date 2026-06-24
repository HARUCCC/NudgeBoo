import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from ghost_widget import GhostWidget
from log_panel import LogPanel
from timeline import Timeline
from config import load_config, save_config


def get_icon():
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    ico_path = os.path.join(base, "app.ico")
    if os.path.exists(ico_path):
        return QIcon(ico_path)
    return QIcon()


class NudgeBooApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.icon = get_icon()
        self.app.setWindowIcon(self.icon)
        self.cfg = load_config()

        self.timeline = Timeline()
        self._is_dnd = self.cfg.get("dnd_mode", False)

        # Ghost widget
        self.ghost = GhostWidget()
        self.ghost.setFixedSize(130, 160)
        self.ghost.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.ghost.setAttribute(Qt.WA_TranslucentBackground)
        self.ghost.setWindowIcon(self.icon)

        # Position at bottom-right
        screen = self.app.primaryScreen().geometry()
        self._base_x = screen.width() - 130 - 20
        self._base_y = screen.height() - 160 - 60
        self.ghost.move(self._base_x, self._base_y)

        if not self._is_dnd:
            self.ghost.show()

        # Log panel (hidden)
        self.log_panel = None

        # Tray
        self.tray = QSystemTrayIcon(self.icon, self.app)
        self.tray_menu = QMenu()

        self.action_record = QAction("开始记录", self.tray_menu)
        self.action_record.triggered.connect(self._toggle_recording)
        self.tray_menu.addAction(self.action_record)

        self.action_panel = QAction("打开日志面板", self.tray_menu)
        self.action_panel.triggered.connect(self._show_log_panel)
        self.tray_menu.addAction(self.action_panel)

        self.tray_menu.addSeparator()

        action_quit = QAction("退出", self.tray_menu)
        action_quit.triggered.connect(self._quit)
        self.tray_menu.addAction(action_quit)

        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

        # Ghost interactions
        self.ghost.double_clicked.connect(self._show_log_panel)
        self.ghost.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ghost.customContextMenuRequested.connect(self._show_ghost_menu)

        # State update timer
        self.state_timer = QTimer()
        self.state_timer.timeout.connect(self._update_state)
        self.state_timer.start(5000)

        # Reminder timer
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self._check_reminder)
        self.reminder_timer.start(60000)

        self._last_reminder_shown = False

    def _show_ghost_menu(self, pos):
        menu = QMenu()
        action_record = QAction("停止记录" if self.timeline.recording else "开始记录", menu)
        action_record.triggered.connect(self._toggle_recording)
        menu.addAction(action_record)

        action_panel = QAction("打开日志面板", menu)
        action_panel.triggered.connect(self._show_log_panel)
        menu.addAction(action_panel)

        action_minimize = QAction("最小化到状态栏", menu)
        action_minimize.triggered.connect(self._minimize_to_tray)
        menu.addAction(action_minimize)

        menu.addSeparator()
        action_quit = QAction("退出", menu)
        action_quit.triggered.connect(self._quit)
        menu.addAction(action_quit)

        menu.exec_(self.ghost.mapToGlobal(pos))

    def _toggle_recording(self):
        is_on = self.timeline.toggle_recording()
        if not self._is_dnd:
            self._show_notification(
                "开始记录" if is_on else "停止记录",
                "已开始工作计时，加油！" if is_on else "已停止工作计时"
            )
        self._sync_ui()
        self._update_state()

    def _show_log_panel(self):
        if self.log_panel is None:
            self.log_panel = LogPanel(timeline=self.timeline)
            self.log_panel.setWindowIcon(self.icon)
            self.log_panel.log_saved.connect(self._on_log_saved)
            self.log_panel.recording_toggled.connect(self._on_panel_toggle)
            self.log_panel.dnd_toggled.connect(self._on_dnd_toggle)
        self.log_panel.update_timeline()
        self.log_panel.showNormal()
        self.log_panel.raise_()
        self.log_panel.activateWindow()

    def _minimize_to_tray(self):
        self.ghost.hide()
        if not self._is_dnd:
            self._show_notification("已最小化", "NudgeBoo 已最小化，双击图标恢复")

    def _on_log_saved(self):
        self._last_reminder_shown = False
        self._update_state()

    def _on_panel_toggle(self, is_on):
        if is_on and not self.timeline.recording:
            self.timeline.start_recording()
        elif not is_on and self.timeline.recording:
            self.timeline.stop_recording()
        self._sync_ui()

    def _on_dnd_toggle(self, is_dnd):
        self._is_dnd = is_dnd
        if is_dnd:
            self.ghost.hide()
        else:
            self.ghost.show()
            self.ghost.move(self._base_x, self._base_y)

    def _sync_ui(self):
        is_on = self.timeline.recording
        self.action_record.setText("停止记录" if is_on else "开始记录")
        if self.log_panel:
            self.log_panel.update_toggle(is_on)
            self.log_panel.update_timeline()

    def _update_state(self):
        self.cfg = load_config()
        interval = self.cfg.get("reminder_interval_min", 120)
        state = self.timeline.get_ghost_state(reminder_interval_min=interval)
        self.ghost.set_state(state)

        if self.timeline.recording:
            count = self.timeline.get_record_count_today()
            tip = f"状态: {state} | 今日记录: {count}次"
            if self.timeline.last_record_time:
                lunch_start = self.cfg.get("lunch_start", "12:00")
                lunch_end = self.cfg.get("lunch_end", "13:30")
                mins = self.timeline.minutes_since_last_record(lunch_start, lunch_end)
                tip += f"\n距上次记录: {int(mins)}分钟"
            self.tray.setToolTip(tip)
        else:
            self.tray.setToolTip("NudgeBoo - 点击右键开始记录")

    def _check_reminder(self):
        if not self.timeline.recording or self._is_dnd:
            return
        self.cfg = load_config()
        interval = self.cfg.get("reminder_interval_min", 120)
        lunch_start = self.cfg.get("lunch_start", "12:00")
        lunch_end = self.cfg.get("lunch_end", "13:30")
        mins = self.timeline.minutes_since_last_record(lunch_start, lunch_end)
        if mins >= interval and not self._last_reminder_shown:
            self._show_notification(
                "该记录啦！",
                f"已经 {int(mins)} 分钟没有记录了，打开日志面板写点什么吧！"
            )
            self._last_reminder_shown = True

    def _show_notification(self, title, msg):
        self.tray.showMessage(title, msg, QSystemTrayIcon.Information, 5000)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.ghost.show()
            self.ghost.raise_()
            self.ghost.activateWindow()

    def _quit(self):
        self.app.quit()

    def run(self):
        return self.app.exec_()


if __name__ == "__main__":
    pet = NudgeBooApp()
    sys.exit(pet.run())
