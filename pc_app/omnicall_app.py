from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import qrcode
from PIL.ImageQt import ImageQt
from PyQt6 import QtCore, QtGui, QtWidgets

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import load_config, save_config
from detector import DetectorThread
from firebase_client import (
    DEFAULT_MESSAGE,
    PWA_URL,
    GlobalStats,
    create_user,
    fetch_stats,
    send_notification,
    submit_feedback,
)

APP_NAME = "OmniCall Desktop"


def resource_path(relative: str) -> Path:
    return (BASE_DIR / relative).resolve()


def _load_app_icon() -> QtGui.QIcon:
    for candidate in ("omnicall.ico", "../docs/icon-192.png", "../docs/icon-512.png"):
        path = resource_path(candidate)
        if path.exists():
            return QtGui.QIcon(str(path))
    return QtGui.QIcon()


APP_ICON = _load_app_icon()


def _html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


class RegistrationDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to OmniCall")
        if not APP_ICON.isNull():
            self.setWindowIcon(APP_ICON)
        self.setModal(True)
        self.resize(520, 540)

        self.display_name = ""
        self.user_id = ""
        self.pairing_link = ""
        self.test_confirmed = False

        self.stack = QtWidgets.QStackedWidget()
        self.step_intro = self._build_intro()
        self.step_qr = self._build_qr_step()
        self.stack.addWidget(self.step_intro)
        self.stack.addWidget(self.step_qr)

        self.buttons = QtWidgets.QDialogButtonBox()
        self.finish_btn = self.buttons.addButton("Finish", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_btn = self.buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.finish_btn.setEnabled(False)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.stack)
        layout.addWidget(self.buttons)

    def _build_intro(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("<h2>Register this PC</h2>")
        subtitle = QtWidgets.QLabel(
            "Enter a friendly device name. We will generate a secure pairing code, show a QR to scan on your phone, and keep the unique bits hidden."
        )
        subtitle.setWordWrap(True)

        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("e.g., Khaled's PC")

        self.error_label = QtWidgets.QLabel()
        self.error_label.setStyleSheet("color:#ff6b6b;")

        self.create_btn = QtWidgets.QPushButton("Generate Pairing QR")
        self.create_btn.clicked.connect(self._handle_create_user)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(QtWidgets.QLabel("Display name"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.error_label)
        layout.addStretch(1)
        layout.addWidget(self.create_btn)
        return w

    def _build_qr_step(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(12)

        self.hello_label = QtWidgets.QLabel()
        self.hello_label.setWordWrap(True)

        self.qr_label = QtWidgets.QLabel()
        self.qr_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumSize(260, 260)

        self.link_field = QtWidgets.QLineEdit()
        self.link_field.setReadOnly(True)

        copy_btn = QtWidgets.QPushButton("Copy Link")
        copy_btn.clicked.connect(self._copy_link)

        self.test_btn = QtWidgets.QPushButton("Send Test Notification")
        self.test_btn.clicked.connect(self._send_test)

        self.test_status = QtWidgets.QLabel()
        self.test_status.setWordWrap(True)

        self.confirm_btn = QtWidgets.QPushButton("I received the notification")
        self.confirm_btn.clicked.connect(self._confirm_test)
        self.confirm_btn.setEnabled(False)

        instructions = QtWidgets.QLabel(
            "1. Scan the QR with your phone.\n2. Install the PWA (Add to Home Screen).\n3. Tap Enable Notifications in the PWA."
        )
        instructions.setWordWrap(True)

        layout.addWidget(self.hello_label)
        layout.addWidget(self.qr_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QtWidgets.QLabel("Pairing link"))
        layout.addWidget(self.link_field)
        layout.addWidget(copy_btn)
        layout.addWidget(self.test_btn)
        layout.addWidget(self.test_status)
        layout.addWidget(self.confirm_btn)
        layout.addWidget(instructions)
        layout.addStretch(1)
        return w

    def _handle_create_user(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("Display name is required.")
            return
        self.create_btn.setEnabled(False)
        self.error_label.clear()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            uid, link = create_user(name)
        except Exception as exc:
            self.error_label.setText(f"Failed to create user: {exc}")
            self.create_btn.setEnabled(True)
            QtWidgets.QApplication.restoreOverrideCursor()
            return
        QtWidgets.QApplication.restoreOverrideCursor()

        self.display_name = name
        self.user_id = uid
        self.pairing_link = link
        safe_name = _html_escape(name)
        self.hello_label.setText(f"<h3>Hello, {safe_name}!</h3> Scan this QR to pair your phone.")
        self._render_qr()
        self.link_field.setText(link)
        self.test_status.setText("Send a test notification once pairing is complete.")
        self.confirm_btn.setEnabled(False)
        self.finish_btn.setEnabled(False)
        self.stack.setCurrentWidget(self.step_qr)

    def _render_qr(self) -> None:
        if not self.pairing_link:
            return
        qr_img = qrcode.make(self.pairing_link).convert("RGB")
        qt_img = ImageQt(qr_img)
        pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(qt_img))
        scaled = pixmap.scaled(280, 280, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.qr_label.setPixmap(scaled)

    def _copy_link(self) -> None:
        if not self.pairing_link:
            return
        QtWidgets.QApplication.clipboard().setText(self.pairing_link)
        self.test_status.setText("Link copied. Scan it from your phone if QR is inconvenient.")

    def _send_test(self) -> None:
        if not self.user_id:
            self.test_status.setText("Create the pairing first.")
            return
        self.test_btn.setEnabled(False)
        self.test_status.setText("Sending test notification...")
        QtWidgets.QApplication.processEvents()
        try:
            result = send_notification(self.user_id, "Hello from OmniCall Desktop! (test)")
        except Exception as exc:
            self.test_status.setText(f"Failed to send: {exc}")
            self.test_btn.setEnabled(True)
            return
        if result.sent:
            self.test_status.setText("Test notification sent. Confirm after you see it on your phone.")
            self.confirm_btn.setEnabled(True)
        else:
            reason = result.failures[0] if result.failures else "Unknown error"
            self.test_status.setText(f"No tokens available: {reason}")
            self.test_btn.setEnabled(True)

    def _confirm_test(self) -> None:
        self.test_confirmed = True
        self.finish_btn.setEnabled(True)
        self.test_status.setText("Great! Notifications are confirmed.")


class PairingDialog(QtWidgets.QDialog):
    def __init__(self, display_name: str, link: str, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Pair another phone")
        if not APP_ICON.isNull():
            self.setWindowIcon(APP_ICON)
        self.resize(420, 480)
        layout = QtWidgets.QVBoxLayout(self)

        safe_name = _html_escape(display_name)
        layout.addWidget(QtWidgets.QLabel(f"<h3>{safe_name}</h3> Scan to pair."))

        qr_img = qrcode.make(link).convert("RGB")
        qt_img = ImageQt(qr_img)
        pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(qt_img))
        label = QtWidgets.QLabel(alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setPixmap(
            pixmap.scaled(
                280,
                280,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
        )
        layout.addWidget(label)

        link_field = QtWidgets.QLineEdit(link)
        link_field.setReadOnly(True)
        layout.addWidget(link_field)

        copy_btn = QtWidgets.QPushButton("Copy link")
        copy_btn.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(link))
        layout.addWidget(copy_btn)
        layout.addStretch(1)


class MainWindow(QtWidgets.QMainWindow):
    sendResult = QtCore.pyqtSignal(int, int)
    statusMessage = QtCore.pyqtSignal(str)

    def __init__(self, cfg: dict) -> None:
        super().__init__()
        self.cfg = cfg
        self.detector: Optional[DetectorThread] = None
        self.setWindowTitle(APP_NAME)
        if not APP_ICON.isNull():
            self.setWindowIcon(APP_ICON)
        self.resize(720, 520)

        self.tabs = QtWidgets.QTabWidget()
        self.tab_primary = self._build_primary_tab()
        self.tab_stats = self._build_stats_tab()
        self.tab_feedback = self._build_feedback_tab()
        self.tab_support = self._build_support_tab()

        self.tabs.addTab(self.tab_primary, "Tracking")
        self.tabs.addTab(self.tab_stats, "Statistics")
        self.tabs.addTab(self.tab_feedback, "Feedback")
        self.tabs.addTab(self.tab_support, "Support")
        self.setCentralWidget(self.tabs)

        self.sendResult.connect(self._handle_send_result)
        self.statusMessage.connect(self._show_status)

        self.statusBar().showMessage("Ready")
        self._refresh_stats()
        self._update_primary_state()

        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_stats)
        self.refresh_timer.start(120_000)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self._stop_detector()
        super().closeEvent(event)

    # Primary tab ---------------------------------------------------------
    def _build_primary_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(12)

        safe_name = _html_escape(self.cfg["display_name"])
        hello = QtWidgets.QLabel(f"<h2>Hello, {safe_name}</h2>")
        hello.setWordWrap(True)

        info_label = QtWidgets.QLabel(
            "Pairing stays active for this device. Use the buttons below to manage notifications and tracking."
        )
        info_label.setWordWrap(True)

        self.notification_state = QtWidgets.QLabel()

        self.test_button = QtWidgets.QPushButton("Send Test Notification")
        self.test_button.clicked.connect(self._send_test_notification)

        self.toggle_button = QtWidgets.QPushButton("Start Tracking")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self._handle_toggle)

        self.detector_status = QtWidgets.QLabel("Tracking idle")

        default_template = self.cfg.get("template_path") or str(_default_template_path())
        self.template_path = QtWidgets.QLineEdit(default_template)
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(self._choose_template)
        tpl_row = QtWidgets.QHBoxLayout()
        tpl_row.addWidget(self.template_path)
        tpl_row.addWidget(browse_btn)

        self.threshold_spin = QtWidgets.QDoubleSpinBox()
        self.threshold_spin.setRange(0.5, 0.99)
        self.threshold_spin.setSingleStep(0.01)
        self.threshold_spin.setValue(float(self.cfg.get("threshold", 0.8)))

        self.debounce_spin = QtWidgets.QSpinBox()
        self.debounce_spin.setRange(1, 600)
        self.debounce_spin.setValue(int(self.cfg.get("debounce_seconds", 10)))

        self.poll_spin = QtWidgets.QSpinBox()
        self.poll_spin.setRange(50, 2000)
        self.poll_spin.setValue(int(self.cfg.get("poll_ms", 200)))

        grid = QtWidgets.QFormLayout()
        grid.addRow("Template", tpl_row)
        grid.addRow("Threshold", self.threshold_spin)
        grid.addRow("Cooldown (s)", self.debounce_spin)
        grid.addRow("Polling (ms)", self.poll_spin)

        self.last_match_label = QtWidgets.QLabel(self._format_last_match())
        self.total_match_label = QtWidgets.QLabel(str(self.cfg.get("total_matches", 0)))

        stats_grid = QtWidgets.QFormLayout()
        stats_grid.addRow("Last match", self.last_match_label)
        stats_grid.addRow("Total matches sent", self.total_match_label)

        secondary_row = QtWidgets.QHBoxLayout()
        qr_btn = QtWidgets.QPushButton("Show Pairing QR")
        qr_btn.clicked.connect(self._show_pairing)
        secondary_row.addWidget(qr_btn)
        secondary_row.addWidget(self.test_button)
        secondary_row.addStretch(1)

        layout.addWidget(hello)
        layout.addWidget(info_label)
        layout.addWidget(self.notification_state)
        layout.addLayout(secondary_row)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.detector_status)
        layout.addLayout(grid)
        layout.addWidget(QtWidgets.QLabel("Your stats"))
        layout.addLayout(stats_grid)
        layout.addStretch(1)
        return w

    def _update_primary_state(self) -> None:
        confirmed = bool(self.cfg.get("test_confirmed"))
        if confirmed:
            self.notification_state.setText("Notifications confirmed ✔")
            self.toggle_button.setEnabled(True)
        else:
            self.notification_state.setText("Complete the test notification to unlock tracking.")
            self.toggle_button.setEnabled(False)
        self.detector_status.setText("Tracking idle")
        self.toggle_button.setChecked(False)
        self.toggle_button.setText("Start Tracking")

    def _send_test_notification(self) -> None:
        self.statusBar().showMessage("Sending test…")
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            result = send_notification(self.cfg["user_id"], "Desktop test ping")
        except Exception as exc:
            self.statusBar().showMessage(str(exc), 5000)
            QtWidgets.QApplication.restoreOverrideCursor()
            return
        QtWidgets.QApplication.restoreOverrideCursor()
        if result.sent:
            self.statusBar().showMessage("Test notification sent", 4000)
            self.cfg["test_confirmed"] = True
            save_config(self.cfg)
            self._update_primary_state()
        else:
            message = result.failures[0] if result.failures else "No tokens registered"
            self.statusBar().showMessage(message, 6000)

    def _handle_toggle(self) -> None:
        if self.toggle_button.isChecked():
            if not self.cfg.get("test_confirmed"):
                self.statusBar().showMessage("Confirm notifications first", 5000)
                self.toggle_button.setChecked(False)
                return
            self._start_detector()
        else:
            self._stop_detector()

    def _start_detector(self) -> None:
        template = self.template_path.text().strip()
        if not template:
            self.statusBar().showMessage("Choose a template image", 5000)
            self.toggle_button.setChecked(False)
            return
        path = Path(template).expanduser()
        if not path.exists():
            self.statusBar().showMessage("Template not found", 5000)
            self.toggle_button.setChecked(False)
            return
        self.cfg["template_path"] = str(path)
        self.cfg["threshold"] = float(self.threshold_spin.value())
        self.cfg["debounce_seconds"] = int(self.debounce_spin.value())
        self.cfg["poll_ms"] = int(self.poll_spin.value())
        save_config(self.cfg)

        def on_match() -> bool:
            try:
                result = send_notification(self.cfg["user_id"], DEFAULT_MESSAGE)
            except Exception as exc:
                self.statusMessage.emit(f"Send failed: {exc}")
                return False
            self.sendResult.emit(result.sent, result.total)
            return result.sent > 0

        self.detector = DetectorThread(
            template_path=str(path),
            threshold=float(self.threshold_spin.value()),
            debounce_seconds=int(self.debounce_spin.value()),
            poll_ms=int(self.poll_spin.value()),
            on_match=on_match,
        )
        self.detector.match_detected.connect(self._on_match_detected)
        self.detector.status.connect(self._on_detector_status)
        self.detector.finished.connect(self._on_detector_finished)
        self.detector.start()
        self.toggle_button.setText("Stop Tracking")
        self.detector_status.setText("Detector warming up…")
        self.statusBar().showMessage("Tracking started", 4000)

    @QtCore.pyqtSlot(int, int)
    def _handle_send_result(self, sent: int, total: int) -> None:
        if sent > 0:
            self.statusBar().showMessage("Notification sent", 4000)
            self.cfg["total_matches"] = int(self.cfg.get("total_matches", 0)) + sent
            self.cfg["last_match_ts"] = datetime.utcnow().isoformat()
            save_config(self.cfg)
            self.last_match_label.setText(self._format_last_match())
            self.total_match_label.setText(str(self.cfg["total_matches"]))
        else:
            self.statusBar().showMessage("No tokens to send", 6000)

    @QtCore.pyqtSlot(str)
    def _on_detector_status(self, message: str) -> None:
        self.detector_status.setText(message)

    @QtCore.pyqtSlot()
    def _on_detector_finished(self) -> None:
        self.toggle_button.setChecked(False)
        self.toggle_button.setText("Start Tracking")
        self.detector_status.setText("Tracking idle")
        self.statusBar().showMessage("Tracking stopped", 4000)
        self.detector = None

    @QtCore.pyqtSlot(float)
    def _on_match_detected(self, score: float) -> None:
        self.detector_status.setText(f"Match detected (score {score:.3f})")

    @QtCore.pyqtSlot(str)
    def _show_status(self, message: str) -> None:
        self.statusBar().showMessage(message, 6000)

    def _stop_detector(self) -> None:
        if self.detector and self.detector.isRunning():
            self.detector.stop()
            self.detector.wait(2000)
        self.detector = None
        self.toggle_button.setChecked(False)
        self.toggle_button.setText("Start Tracking")
        self.detector_status.setText("Tracking idle")

    def _choose_template(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose template", str(Path.home()), "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.template_path.setText(file_path)
            self.cfg["template_path"] = file_path
            save_config(self.cfg)

    def _show_pairing(self) -> None:
        dlg = PairingDialog(self.cfg.get("display_name", ""), self.cfg.get("pairing_link", PWA_URL), self)
        dlg.exec()

    def _format_last_match(self) -> str:
        ts = self.cfg.get("last_match_ts")
        if not ts:
            return "Never"
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError:
            return ts
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    # Stats tab -----------------------------------------------------------
    def _build_stats_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(12)

        self.global_users = QtWidgets.QLabel("0")
        self.global_sends = QtWidgets.QLabel("0")
        self.global_today = QtWidgets.QLabel("0")

        refresh_btn = QtWidgets.QPushButton("Refresh now")
        refresh_btn.clicked.connect(self._refresh_stats)

        grid = QtWidgets.QFormLayout()
        grid.addRow("Total users", self.global_users)
        grid.addRow("Notifications sent", self.global_sends)
        grid.addRow("Users registered today", self.global_today)

        layout.addWidget(QtWidgets.QLabel("<h3>OmniCall community stats</h3>"))
        layout.addLayout(grid)
        layout.addWidget(refresh_btn)
        layout.addStretch(1)
        return w

    def _refresh_stats(self) -> None:
        try:
            stats = fetch_stats()
        except Exception as exc:
            self.statusBar().showMessage(f"Stats unavailable: {exc}", 6000)
            return
        self._apply_stats(stats)

    def _apply_stats(self, stats: GlobalStats) -> None:
        self.global_users.setText(str(stats.total_users))
        self.global_sends.setText(str(stats.total_sends))
        self.global_today.setText(str(stats.users_today))

    # Feedback tab --------------------------------------------------------
    def _build_feedback_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(12)

        self.feedback_edit = QtWidgets.QPlainTextEdit()
        self.feedback_edit.setPlaceholderText("Tell us what to improve or report issues…")
        submit_btn = QtWidgets.QPushButton("Submit feedback")
        submit_btn.clicked.connect(self._submit_feedback)
        self.feedback_status = QtWidgets.QLabel()

        layout.addWidget(QtWidgets.QLabel("<h3>We love feedback</h3>"))
        layout.addWidget(self.feedback_edit)
        layout.addWidget(submit_btn)
        layout.addWidget(self.feedback_status)
        layout.addStretch(1)
        return w

    def _submit_feedback(self) -> None:
        text = self.feedback_edit.toPlainText().strip()
        if not text:
            self.feedback_status.setText("Enter some feedback first.")
            return
        try:
            submit_feedback(self.cfg["user_id"], self.cfg.get("display_name", ""), text)
        except Exception as exc:
            self.feedback_status.setText(f"Failed to submit: {exc}")
            return
        self.feedback_edit.clear()
        self.feedback_status.setText("Thanks! Feedback sent.")

    # Support tab --------------------------------------------------------
    def _build_support_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(10)

        text = QtWidgets.QLabel(
            "<h3>Support the creator</h3>" \
            "If OmniCall helps you, consider buying a coffee."
        )
        text.setWordWrap(True)

        binance = QtWidgets.QLabel("<b>Binance</b><br>Email: amrkhaled272@gmail.com<br>ID: 753805136")
        paypal = QtWidgets.QLabel("<b>PayPal</b><br>Email: amrkhaled122@aucegypt.edu")
        for lbl in (binance, paypal):
            lbl.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

        layout.addWidget(text)
        layout.addWidget(binance)
        layout.addWidget(paypal)
        layout.addStretch(1)
        return w


def _default_template_path() -> Path:
    for candidate in ("../Accept.png", "Accept.png"):
        path = resource_path(candidate)
        if path.exists():
            return path
    return Path.home()


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setApplicationName(APP_NAME)
    if not APP_ICON.isNull():
        app.setWindowIcon(APP_ICON)

    cfg = load_config()
    if not cfg.get("user_id"):
        wizard = RegistrationDialog()
        if wizard.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return 0
        cfg["display_name"] = wizard.display_name
        cfg["user_id"] = wizard.user_id
        cfg["pairing_link"] = wizard.pairing_link
        cfg["test_confirmed"] = wizard.test_confirmed
        save_config(cfg)

    window = MainWindow(cfg)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
