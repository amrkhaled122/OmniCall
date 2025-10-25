from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable, Optional

import cv2  # type: ignore
import mss  # type: ignore
import numpy as np
from PyQt6 import QtCore


class DetectorThread(QtCore.QThread):
    match_detected = QtCore.pyqtSignal(float)
    status = QtCore.pyqtSignal(str)

    def __init__(self, template_path: str, threshold: float, debounce_seconds: int, poll_ms: int, on_match: Callable[[], bool], parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self.template_path = template_path
        self.threshold = threshold
        self.debounce_seconds = debounce_seconds
        self.poll_ms = poll_ms
        self._stop_signal = threading.Event()
        self._on_match = on_match

    def stop(self) -> None:
        self._stop_signal.set()

    def run(self) -> None:
        try:
            templ = _load_template(self.template_path)
        except Exception as exc:
            self.status.emit(f"Template error: {exc}")
            return

        cooldown_until = 0.0
        self.status.emit("Detector running")
        while not self._stop_signal.is_set():
            now = time.time()
            try:
                if now >= cooldown_until:
                    screen = _capture_screen_bgr()
                    score = _template_score(screen, templ)
                    if score >= self.threshold:
                        self.match_detected.emit(score)
                        success = False
                        try:
                            success = self._on_match()
                        except Exception as exc:
                            self.status.emit(f"Send error: {exc}")
                        cooldown = self.debounce_seconds if success else 3
                        cooldown_until = time.time() + max(1, cooldown)
                time.sleep(max(0.01, self.poll_ms / 1000.0))
            except Exception as exc:
                self.status.emit(f"Detector error: {exc}")
                time.sleep(1)
        self.status.emit("Detector stopped")


def _load_template(path: str) -> np.ndarray:
    resolved = Path(path).expanduser().resolve()
    templ = cv2.imread(str(resolved), cv2.IMREAD_COLOR)
    if templ is None:
        raise FileNotFoundError(f"Template not found: {resolved}")
    return templ


def _capture_screen_bgr() -> np.ndarray:
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        raw = np.array(sct.grab(monitor))
    return cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)


def _template_score(screen: np.ndarray, templ: np.ndarray) -> float:
    if screen.shape[0] < templ.shape[0] or screen.shape[1] < templ.shape[1]:
        return 0.0
    res = cv2.matchTemplate(screen, templ, cv2.TM_CCOEFF_NORMED)
    _min_val, max_val, _min_loc, _max_loc = cv2.minMaxLoc(res)
    return float(max_val)
