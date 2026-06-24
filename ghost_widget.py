from PyQt5.QtCore import Qt, QPointF, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt5.QtWidgets import QWidget


class GhostWidget(QWidget):
    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "idle"
        self._drag_pos = None
        self._poke = False
        self._click_timer = QTimer()
        self._click_timer.setSingleShot(True)
        self._click_timer.setInterval(250)
        self._click_timer.timeout.connect(self._on_single_click)

    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if self._poke:
            self._draw_poked(p)
        else:
            {
                "idle": self._draw_idle,
                "happy": self._draw_happy,
                "alert": self._draw_alert,
                "tired": self._draw_tired,
            }.get(self.state, self._draw_normal)(p)

    # ─── Ghost ──────────────────────────────────────────────

    def _draw_ghost(self, p, y_off=0, eye_style="open", blush=False, mouth_style="default"):
        p.save()
        p.translate(0, y_off)
        p.setPen(Qt.NoPen)

        ghost_c = QColor(240, 240, 255, 220)
        ghost_h = QColor(255, 255, 255, 240)

        # Body
        body = QPainterPath()
        body.moveTo(25, 110)
        body.cubicTo(25, 60, 35, 25, 65, 20)
        body.cubicTo(95, 25, 105, 60, 105, 110)
        body.cubicTo(105, 118, 98, 125, 90, 130)
        body.cubicTo(82, 125, 78, 135, 72, 140)
        body.cubicTo(66, 135, 60, 125, 52, 130)
        body.cubicTo(44, 125, 38, 135, 30, 140)
        body.cubicTo(25, 130, 25, 120, 25, 110)
        p.setBrush(ghost_c)
        p.drawPath(body)

        # Highlight
        p.setBrush(ghost_h)
        highlight = QPainterPath()
        highlight.moveTo(35, 50)
        highlight.cubicTo(32, 70, 35, 90, 40, 100)
        highlight.cubicTo(38, 85, 36, 65, 35, 50)
        p.drawPath(highlight)

        # Eyes
        for cx in [52, 78]:
            cy = 75
            if eye_style == "open":
                p.setBrush(QColor(40, 40, 60))
                p.drawEllipse(cx - 7, cy - 8, 14, 16)
                p.setBrush(QColor(80, 80, 120))
                p.drawEllipse(cx - 5, cy - 6, 10, 13)
                p.setBrush(QColor(20, 20, 40))
                p.drawEllipse(cx - 3, cy - 4, 6, 10)
                p.setBrush(QColor(255, 255, 255, 200))
                p.drawEllipse(cx + 1, cy - 3, 4, 4)
                p.setBrush(QColor(255, 255, 255, 120))
                p.drawEllipse(cx - 2, cy + 2, 3, 3)
            elif eye_style == "closed":
                p.setPen(QPen(QColor(40, 40, 60), 2, Qt.SolidLine, Qt.RoundCap))
                arc = QPainterPath()
                arc.moveTo(cx - 6, cy)
                arc.quadTo(QPointF(cx, cy + 5), QPointF(cx + 6, cy))
                p.drawPath(arc)
                p.setPen(Qt.NoPen)
            elif eye_style == "half":
                p.setBrush(QColor(40, 40, 60))
                p.drawEllipse(cx - 5, cy, 10, 8)
                p.setBrush(QColor(240, 240, 255, 220))
                p.drawEllipse(cx - 6, cy - 4, 12, 8)

        # Blush
        if blush:
            p.setBrush(QColor(255, 150, 150, 60))
            p.drawEllipse(38, 88, 12, 8)
            p.drawEllipse(80, 88, 12, 8)

        # Mouth
        if mouth_style == "tired":
            p.setPen(QPen(QColor(60, 60, 80), 1.5, Qt.SolidLine, Qt.RoundCap))
            m = QPainterPath()
            m.moveTo(58, 96)
            m.quadTo(QPointF(61, 93), QPointF(65, 96))
            m.quadTo(QPointF(69, 99), QPointF(72, 96))
            p.drawPath(m)
            p.setPen(Qt.NoPen)
        elif eye_style == "closed":
            p.setPen(QPen(QColor(60, 60, 80), 1.5, Qt.SolidLine, Qt.RoundCap))
            m = QPainterPath()
            m.moveTo(58, 95)
            m.quadTo(QPointF(65, 100), QPointF(72, 95))
            p.drawPath(m)
            p.setPen(Qt.NoPen)
        else:
            p.setBrush(QColor(60, 60, 80))
            p.drawEllipse(62, 93, 6, 7)

        p.restore()

    # ─── States ──────────────────────────────────────────────

    def _draw_normal(self, p):
        self._draw_ghost(p, eye_style="open")

    def _draw_happy(self, p):
        self._draw_ghost(p, eye_style="closed", blush=True)

    def _draw_alert(self, p):
        self._draw_ghost(p, eye_style="open")
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 100, 100))
        p.drawRoundedRect(62, 5, 6, 14, 3, 3)
        p.drawEllipse(62, 22, 6, 6)

    def _draw_idle(self, p):
        self._draw_ghost(p, eye_style="closed")

    def _draw_tired(self, p):
        self._draw_ghost(p, eye_style="half", mouth_style="tired", blush=True)

    def _draw_poked(self, p):
        self._draw_ghost(p, y_off=-8, eye_style="open")
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 200, 50))
        p.drawRoundedRect(60, 2, 8, 16, 3, 3)
        p.drawEllipse(60, 22, 8, 8)
        p.setBrush(QColor(255, 255, 150))
        for sx, sy in [(20, 30), (105, 25), (18, 80)]:
            p.drawEllipse(sx, sy, 5, 5)

    def _end_poke(self):
        self._poke = False
        self.update()

    # ─── Drag & Poke ────────────────────────────────────────

    def _on_single_click(self):
        """Triggered on single click (after timer confirms no double click)."""
        self._poke = True
        self.update()
        QTimer.singleShot(800, self._end_poke)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()
            self._click_timer.start()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._click_timer.stop()  # Cancel single click
            self.double_clicked.emit()
            event.accept()
