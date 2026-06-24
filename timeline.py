from datetime import datetime, timedelta
import json
import os
import sys

if getattr(sys, 'frozen', False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(_BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)
TIMELINE_FILE = os.path.join(DATA_DIR, "timeline.json")


class Timeline:
    def __init__(self):
        self.work_start = None
        self.recording = False
        self.last_record_time = None
        self.entries_today = []
        self._load_state()

    def _load_state(self):
        if not os.path.exists(TIMELINE_FILE):
            return
        try:
            with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            saved_date = data.get("date", "")
            today = datetime.now().strftime("%Y-%m-%d")
            if saved_date != today:
                return  # New day, start fresh
            self.recording = data.get("recording", False)
            if data.get("work_start"):
                self.work_start = datetime.fromisoformat(data["work_start"])
            if data.get("last_record_time"):
                self.last_record_time = datetime.fromisoformat(data["last_record_time"])
            self.entries_today = data.get("entries_today", [])
        except:
            pass

    def _save_state(self):
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "recording": self.recording,
            "work_start": self.work_start.isoformat() if self.work_start else None,
            "last_record_time": self.last_record_time.isoformat() if self.last_record_time else None,
            "entries_today": self.entries_today,
        }
        try:
            with open(TIMELINE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def start_recording(self):
        now = datetime.now()
        if self.work_start is None or now.date() != self.work_start.date():
            self.entries_today = []
            self.work_start = now
        self.recording = True
        self.last_record_time = now
        self._save_state()

    def stop_recording(self):
        self.recording = False
        self._save_state()

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()
        return self.recording

    def record_entry(self, content):
        now = datetime.now()
        self.entries_today.append((now.strftime("%H:%M"), content))
        self.last_record_time = now
        self._save_state()

    def get_progress_info(self, cfg):
        """Return (progress%, (start_time, end_time), entry_times, overtime%)."""
        now = datetime.now()
        work_mode = cfg.get("work_mode", "fixed")

        if work_mode == "fixed":
            sh, sm = map(int, cfg.get("work_start", "09:00").split(":"))
            eh, em = map(int, cfg.get("work_end", "18:00").split(":"))
            work_start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
            work_end = now.replace(hour=eh, minute=em, second=0, microsecond=0)
        else:
            if not self.work_start:
                return 0, None, [], 0
            work_start = self.work_start.replace(second=0, microsecond=0)
            hours = cfg.get("work_duration", 9)
            work_end = work_start + timedelta(hours=hours)

        normal_sec = (work_end - work_start).total_seconds()
        if normal_sec <= 0:
            return 0, None, [], 0

        # Find the latest entry time to determine display range
        today = now.date()
        latest_entry = work_end
        for time_str, _ in self.entries_today:
            h, m = map(int, time_str.split(":"))
            entry_time = datetime.combine(today, datetime.min.time().replace(hour=h, minute=m))
            if entry_time > latest_entry:
                latest_entry = entry_time

        # Display end: at least work_end, extend to latest entry + buffer
        if latest_entry > work_end:
            display_end = latest_entry + timedelta(minutes=30)
        else:
            display_end = work_end

        # Overtime = how much past work_end in the display
        overtime_sec = max(0, (display_end - work_end).total_seconds())
        overtime_pct = round(overtime_sec / normal_sec * 100) if normal_sec > 0 else 0

        # Normal progress (capped at 100%)
        elapsed = min((now - work_start).total_seconds(), normal_sec)
        progress = int(elapsed / normal_sec * 100)

        full_sec = (display_end - work_start).total_seconds()

        entry_times = []  # (position%, time_str, is_overtime)
        seen_pos = set()
        for time_str, _ in self.entries_today:
            h, m = map(int, time_str.split(":"))
            entry_time = datetime.combine(today, datetime.min.time().replace(hour=h, minute=m))
            if work_start <= entry_time <= display_end:
                pos = round((entry_time - work_start).total_seconds() / full_sec * 100, 1)
                if any(abs(pos - p) < 1 for p in seen_pos):
                    continue
                seen_pos.add(pos)
                is_ot = entry_time > work_end
                entry_times.append((pos, time_str, is_ot))

        normal_ratio = round(normal_sec / full_sec * 100) if full_sec > 0 else 100
        return progress, (work_start, work_end), entry_times, overtime_pct, normal_ratio

    def get_record_count_today(self):
        return len(self.entries_today)

    def minutes_since_last_record(self, lunch_start_str="12:00", lunch_end_str="13:30"):
        if self.last_record_time is None:
            return 0
        now = datetime.now()
        total_min = (now - self.last_record_time).total_seconds() / 60

        # Subtract lunch break if it overlaps with the interval
        today = now.date()
        lh, lm = map(int, lunch_start_str.split(":"))
        lunch_start = datetime.combine(today, datetime.min.time().replace(hour=lh, minute=lm))
        lh, lm = map(int, lunch_end_str.split(":"))
        lunch_end = datetime.combine(today, datetime.min.time().replace(hour=lh, minute=lm))

        last = self.last_record_time
        # Calculate overlap between [last, now] and [lunch_start, lunch_end]
        overlap_start = max(last, lunch_start)
        overlap_end = min(now, lunch_end)
        if overlap_end > overlap_start:
            lunch_min = (overlap_end - overlap_start).total_seconds() / 60
            total_min -= lunch_min

        return max(0, total_min)

    def get_ghost_state(self, reminder_interval_min=120):
        if not self.recording:
            return "idle"
        count = self.get_record_count_today()
        minutes = self.minutes_since_last_record()
        if minutes > reminder_interval_min:
            return "alert"
        if count >= 4:
            return "happy"
        if count >= 2:
            return "normal"
        return "tired"
