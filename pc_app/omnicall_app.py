from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Suppress gRPC/ALTS warnings before importing any Firebase libraries
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = ''
os.environ['GLOG_minloglevel'] = '2'
os.environ['GOOGLE_API_USE_CLIENT_CERTIFICATE'] = 'false'
os.environ['GOOGLE_APPLICATION_CREDENTIALS_USE_ALTS'] = 'false'

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
    warmup_cache,
    refresh_token_cache,
)

APP_NAME = "OmniCall Desktop"
FONT_FAMILY = "Segoe UI"

APP_STYLE = """
QMainWindow, QDialog {
    background-color: #0f1115;
    color: #e7ecf3;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}
QWidget#MainSurface {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f1115, stop:1 #141822);
}
QFrame#HeroCard {
    background: rgba(27, 33, 48, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
}
QFrame#Card {
    background: rgba(21, 27, 40, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
}
QFrame#CardSection {
    background: transparent;
}
QFrame#StatBox {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
}
QFrame#SupportItem {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
}
QLabel#SupportArt {
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.04);
}
QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 12px;
    background: rgba(17, 21, 31, 0.9);
}
QTabBar::tab {
    color: #a9b3c7;
    padding: 10px 18px;
    margin-right: 6px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    background: transparent;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: rgba(76, 175, 80, 0.18);
    color: #ffffff;
}
QTabBar::tab:hover {
    background: rgba(76, 175, 80, 0.12);
}
QStatusBar {
    background: transparent;
    color: #a9b3c7;
}
QStatusBar::item {
    border: none;
}
QLabel[variant="subtle"] {
    color: #a9b3c7;
}
QLabel[variant="danger"] {
    color: #ff6b6b;
}
QLabel[variant="success"] {
    color: #8be9a5;
    font-weight: 600;
}
QLabel[role="heading"] {
    font-size: 18px;
    font-weight: 650;
}
QLabel[role="heroTitle"] {
    font-size: 22px;
    font-weight: 700;
}
QLabel[role="section"] {
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-size: 11px;
    color: #7d89a3;
    font-weight: 600;
}
QLabel[role="pill"] {
    background: rgba(76, 175, 80, 0.22);
    border-radius: 14px;
    padding: 6px 14px;
    font-weight: 600;
    color: #c7ffcf;
}
QLabel[role="formLabel"] {
    color: #8d99b8;
    font-weight: 600;
    letter-spacing: 0.2px;
    margin-right: 6px;
}
QLabel[role="statusChip"] {
    padding: 6px 12px;
    border-radius: 14px;
    font-weight: 600;
    letter-spacing: 0.4px;
}
QLabel[role="statusChip"][state="off"] {
    background: rgba(255, 255, 255, 0.08);
    color: #a9b3c7;
}
QLabel[role="statusChip"][state="on"] {
    background: #4caf50;
    color: #0f1115;
}
QLabel[role="statValue"] {
    font-size: 24px;
    font-weight: 700;
}
QLabel[role="statLabel"] {
    color: #a9b3c7;
    font-weight: 500;
}
QLabel[role="supportLabel"] {
    font-weight: 600;
    letter-spacing: 0.2px;
}
QLabel#SupportGlyph {
    color: #0f1115;
    font-weight: 700;
    border-radius: 20px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    qproperty-alignment: 'AlignCenter';
}
QPushButton {
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
}
QPushButton[variant="primary"] {
    background: #4caf50;
    color: white;
    border: none;
}
QPushButton[variant="primary"]:hover {
    background: #45a049;
}
QPushButton[variant="outline"] {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #e7ecf3;
}
QPushButton[variant="outline"]:hover {
    background: rgba(255, 255, 255, 0.08);
}
QPushButton[variant="accent"] {
    background: #4caf50;
    color: white;
    border: none;
}
QPushButton[variant="accent"]:hover {
    background: #3f8f44;
}
QPushButton[variant="accent"]:checked {
    background: #2f7f36;
}
QPushButton[variant="accent"]:checked:hover {
    background: #296f31;
}
QPushButton[variant="toggle"] {
    background: #dc3545;
    color: white;
    border: none;
    font-weight: 600;
}
QPushButton[variant="toggle"]:hover {
    background: #c82333;
}
QPushButton[variant="toggle"]:checked {
    background: #4caf50;
}
QPushButton[variant="toggle"]:checked:hover {
    background: #45a049;
}
QPushButton[variant="ghost"] {
    background: rgba(255, 255, 255, 0.05);
    border: none;
    color: #e7ecf3;
}
QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
    background: rgba(20, 24, 34, 0.86);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 12px;
    padding: 8px 12px;
    color: #e7ecf3;
}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: rgba(76, 175, 80, 0.6);
}
QDoubleSpinBox::up-button, QSpinBox::up-button, QDoubleSpinBox::down-button, QSpinBox::down-button {
    background: transparent;
}
QScrollArea, QScrollArea QWidget {
    background: transparent;
}
QDialogButtonBox QPushButton {
    min-width: 120px;
}
"""

FEEDBACK_WORD_LIMIT = 2000


def resource_path(relative: str) -> Path:
    return (BASE_DIR / relative).resolve()


def _load_app_icon() -> QtGui.QIcon:
    for candidate in (
        "omnicall.ico",
        "icon-192.png",
        "icon-512.png",
        "docs/icon-192.png",
        "docs/icon-512.png",
        "../docs/icon-192.png",
        "../docs/icon-512.png",
    ):
        path = resource_path(candidate)
        if path.exists():
            return QtGui.QIcon(str(path))
    return QtGui.QIcon()


def _load_tab_icon(filename: str) -> QtGui.QIcon:
    """Load a tab icon from the pc_app directory or relative paths."""
    for candidate in (
        filename,
        f"pc_app/{filename}",
        f"../pc_app/{filename}",
    ):
        path = resource_path(candidate)
        if path.exists():
            return QtGui.QIcon(str(path))
    return QtGui.QIcon()


APP_ICON = QtGui.QIcon()


def _make_cash_icon(size: int = 28) -> QtGui.QIcon:
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)

    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    painter.setBrush(QtGui.QColor("#4caf50"))
    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    painter.drawRoundedRect(2, 2, size - 4, size - 4, 8, 8)

    painter.setPen(QtGui.QColor("#0f1115"))
    font = painter.font()
    font.setBold(True)
    font.setPointSize(max(10, int(size * 0.5)))
    painter.setFont(font)
    painter.drawText(pixmap.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, "$")
    painter.end()

    return QtGui.QIcon(pixmap)


def _apply_property(widget: QtWidgets.QWidget, name: str, value: str) -> None:
    widget.setProperty(name, value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def _style_button(button: QtWidgets.QAbstractButton, variant: str = "primary") -> None:
    if button is None:
        return
    _apply_property(button, "variant", variant)
    button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    button.setMinimumHeight(36)


def _create_card() -> QtWidgets.QFrame:
    frame = QtWidgets.QFrame()
    frame.setObjectName("Card")
    layout = QtWidgets.QVBoxLayout(frame)
    layout.setContentsMargins(18, 16, 18, 16)
    layout.setSpacing(12)
    return frame


def _make_stat_box(value_label: QtWidgets.QLabel, caption: str) -> QtWidgets.QFrame:
    box = QtWidgets.QFrame()
    box.setObjectName("StatBox")
    box.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
    layout = QtWidgets.QVBoxLayout(box)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(6)
    value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(value_label)
    caption_label = QtWidgets.QLabel(caption)
    caption_label.setWordWrap(True)
    caption_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    _apply_property(caption_label, "role", "statLabel")
    layout.addWidget(caption_label)
    return box


def _form_label(text: str) -> QtWidgets.QLabel:
    label = QtWidgets.QLabel(text)
    _apply_property(label, "role", "formLabel")
    return label


def _support_badge(glyph: str, color: str) -> QtWidgets.QLabel:
    base = QtGui.QColor(color)
    top_color = base.lighter(140).name()
    bottom_color = base.darker(115).name()

    label = QtWidgets.QLabel(glyph)
    label.setObjectName("SupportGlyph")
    label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    label.setFixedSize(44, 44)
    label.setStyleSheet(
        "color: #0f1115;"
        "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %s, stop:1 %s);"
        % (top_color, bottom_color)
    )
    font = label.font()
    font.setPointSize(14)
    font.setBold(True)
    label.setFont(font)
    label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    return label


def _make_support_item(title: str, detail: str, color: str, glyph: str, logo_file: str = "") -> QtWidgets.QFrame:
    item = QtWidgets.QFrame()
    item.setObjectName("SupportItem")
    item.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
    layout = QtWidgets.QHBoxLayout(item)
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(12)

    # Use logo image if provided, otherwise use text badge
    if logo_file:
        logo_label = QtWidgets.QLabel()
        logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        logo_label.setFixedSize(40, 40)
        
        logo_pixmap = QtGui.QPixmap()
        for rel in (logo_file, f"pc_app/{logo_file}", f"../{logo_file}", f"../pc_app/{logo_file}"):
            path = resource_path(rel)
            if path.exists():
                logo_pixmap = QtGui.QPixmap(str(path))
                break
        
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaled(
                    40, 40,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation,
                )
            )
        layout.addWidget(logo_label, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
    else:
        badge = _support_badge(glyph, color)
        layout.addWidget(badge, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

    text_layout = QtWidgets.QVBoxLayout()
    text_layout.setSpacing(4)
    text_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

    title_label = QtWidgets.QLabel(title)
    title_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
    _apply_property(title_label, "role", "supportLabel")

    detail_label = QtWidgets.QLabel(detail)
    detail_label.setWordWrap(True)
    detail_label.setMinimumWidth(220)
    detail_label.setOpenExternalLinks(True)
    detail_label.setTextInteractionFlags(
        QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        | QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse
    )
    _apply_property(detail_label, "variant", "subtle")

    text_layout.addWidget(title_label)
    text_layout.addWidget(detail_label)
    layout.addLayout(text_layout)
    layout.addStretch(1)
    return item


def _html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _word_count(text: str) -> int:
    if not text:
        return 0
    return len(text.split())


class RegistrationDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to OmniCall")
        if not APP_ICON.isNull():
            self.setWindowIcon(APP_ICON)
        self.setModal(True)
        self.setFixedSize(840, 560)  # Match main window size

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
        self.finish_btn.hide()  # Hide finish button initially
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        # Main layout with same styling as MainWindow
        main_widget = QtWidgets.QWidget()
        main_widget.setObjectName("MainSurface")
        layout = QtWidgets.QVBoxLayout(main_widget)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(16)

        # Add hero card at top (same as main window)
        hero_frame = QtWidgets.QFrame()
        hero_frame.setObjectName("HeroCard")
        hero_layout = QtWidgets.QHBoxLayout(hero_frame)
        hero_layout.setContentsMargins(20, 16, 20, 16)
        hero_layout.setSpacing(14)

        # Icon
        icon_label = QtWidgets.QLabel()
        icon_label.setFixedSize(60, 60)
        icon_pixmap = APP_ICON.pixmap(56, 56)
        if icon_pixmap.isNull():
            icon_pixmap = QtGui.QPixmap(56, 56)
            icon_pixmap.fill(QtGui.QColor("#4caf50"))
        icon_label.setPixmap(icon_pixmap)
        icon_label.setScaledContents(True)

        # Title text
        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(4)
        title = QtWidgets.QLabel(APP_NAME)
        _apply_property(title, "role", "heroTitle")
        tagline = QtWidgets.QLabel("Accept-button tracker with instant push alerts to your phone.")
        tagline.setWordWrap(True)
        _apply_property(tagline, "variant", "subtle")
        text_layout.addWidget(title)
        text_layout.addWidget(tagline)

        hero_layout.addWidget(icon_label)
        hero_layout.addWidget(QtWidgets.QLabel())  # Spacer
        hero_layout.addLayout(text_layout)
        hero_layout.addStretch(1)

        layout.addWidget(hero_frame)

        # Content card
        card = _create_card()
        card.layout().addWidget(self.stack)
        layout.addWidget(card)
        layout.addWidget(self.buttons)

        # Set main widget as dialog's layout
        dialog_layout = QtWidgets.QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(main_widget)

        _style_button(self.finish_btn, "primary")
        _style_button(self.cancel_btn, "outline")

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        """Center the dialog on screen when shown."""
        super().showEvent(event)
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    def _build_intro(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(4, 4, 4, 4)

        title = QtWidgets.QLabel("<h2>Register this PC</h2>")
        _apply_property(title, "role", "heading")
        subtitle = QtWidgets.QLabel(
            "<b>1.</b> Enter a friendly device name<br/>"
            "<b>2.</b> We will generate a secure pairing code<br/>"
            "<b>3.</b> Scan the QR code with your phone<br/>"
            "<b>4.</b> Install the PWA and enable notifications"
        )
        subtitle.setWordWrap(True)
        _apply_property(subtitle, "variant", "subtle")

        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("e.g., Khaled's PC")

        self.error_label = QtWidgets.QLabel()
        _apply_property(self.error_label, "variant", "danger")

        self.create_btn = QtWidgets.QPushButton("Generate Pairing QR")
        self.create_btn.clicked.connect(self._handle_create_user)
        _style_button(self.create_btn, "primary")

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
        main_layout = QtWidgets.QVBoxLayout(w)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(4, 4, 4, 4)

        # Welcome heading
        self.hello_label = QtWidgets.QLabel()
        self.hello_label.setWordWrap(True)
        _apply_property(self.hello_label, "role", "heading")
        main_layout.addWidget(self.hello_label)

        # Content row: Instructions on left, QR on right
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(20)

        # Left side: Instructions and test button
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setSpacing(12)

        instructions = QtWidgets.QLabel(
            "<b>Setup Steps:</b><br/><br/>"
            "1. Scan the QR code with your phone<br/>"
            "2. Install the PWA (Add to Home Screen)<br/>"
            "3. Tap Enable Notifications in the PWA<br/>"
            "4. Send a test notification below<br/>"
            "5. Click Finish after you receive it on the phone"
        )
        instructions.setWordWrap(True)
        _apply_property(instructions, "variant", "subtle")
        left_layout.addWidget(instructions)

        left_layout.addStretch(1)

        self.test_status = QtWidgets.QLabel()
        self.test_status.setWordWrap(True)
        self.test_status.setMinimumHeight(40)
        _apply_property(self.test_status, "variant", "subtle")
        left_layout.addWidget(self.test_status)

        self.test_btn = QtWidgets.QPushButton("Send Test Notification")
        self.test_btn.clicked.connect(self._send_test)
        _style_button(self.test_btn, "primary")
        self.test_btn.setMinimumHeight(44)
        left_layout.addWidget(self.test_btn)

        content_layout.addLayout(left_layout, stretch=1)

        # Right side: QR code frame aligned with steps
        qr_frame = QtWidgets.QFrame()
        qr_frame.setFixedSize(188, 188)
        qr_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: 2px solid rgba(76, 175, 80, 0.4);
                border-radius: 16px;
            }
        """)
        qr_frame_layout = QtWidgets.QVBoxLayout(qr_frame)
        qr_frame_layout.setContentsMargins(2, 2, 2, 2)
        qr_frame_layout.setSpacing(0)

        self.qr_label = QtWidgets.QLabel()
        self.qr_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setFixedSize(184, 184)
        self.qr_label.setStyleSheet("""
            QLabel {
                background: white;
                border-radius: 8px;
            }
        """)
        qr_frame_layout.addWidget(self.qr_label)
        content_layout.addWidget(qr_frame, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(content_layout)
        return w

    def _handle_create_user(self) -> None:
        self.create_btn.setEnabled(False)
        self.error_label.clear()

        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("Enter a display name first.")
            self.create_btn.setEnabled(True)
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            user_id, link = create_user(name)
        except Exception as exc:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.error_label.setText(f"Failed to generate pairing: {exc}")
            self.create_btn.setEnabled(True)
            return
        QtWidgets.QApplication.restoreOverrideCursor()

        self.display_name = name
        self.user_id = user_id
        self.pairing_link = link
        self.test_confirmed = False

        safe = _html_escape(name)
        self.hello_label.setText(f"<h2>Welcome, {safe}</h2>")
        self.test_status.clear()
        self.test_btn.setEnabled(True)
        self.finish_btn.setEnabled(False)

        self._render_qr()
        self.stack.setCurrentWidget(self.step_qr)
        self.finish_btn.show()  # Show finish button on QR step

    def _render_qr(self) -> None:
        if not self.pairing_link:
            return
        qr_img = qrcode.make(self.pairing_link).convert("RGB")
        qt_img = ImageQt(qr_img)
        pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(qt_img))
        scaled = pixmap.scaled(180, 180, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.qr_label.setPixmap(scaled)

    def _send_test(self) -> None:
        if not self.user_id:
            self.test_status.setText("Create the pairing first.")
            _apply_property(self.test_status, "variant", "danger")
            return
        self.test_btn.setEnabled(False)
        self.test_status.setText("Sending test notification...")
        _apply_property(self.test_status, "variant", "subtle")
        QtWidgets.QApplication.processEvents()
        try:
            result = send_notification(self.user_id, "Hello from OmniCall Desktop! (test)")
        except Exception as exc:
            self.test_status.setText(f"Failed to send: {exc}")
            _apply_property(self.test_status, "variant", "danger")
            self.test_btn.setEnabled(True)
            return
        if result.sent:
            self.test_status.setText("✅ Test notification sent! Check your phone, then click Finish.")
            _apply_property(self.test_status, "variant", "success")
            # Enable finish button directly
            self.test_confirmed = True
            self.finish_btn.setEnabled(True)
        else:
            reason = result.failures[0] if result.failures else "Unknown error"
            self.test_status.setText(f"❌ No tokens available: {reason}")
            _apply_property(self.test_status, "variant", "danger")
            self.test_btn.setEnabled(True)


class PairingDialog(QtWidgets.QDialog):
    def __init__(self, display_name: str, link: str, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Pair another phone")
        if not APP_ICON.isNull():
            self.setWindowIcon(APP_ICON)
        self.resize(420, 460)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 18)
        layout.setSpacing(16)

        card = _create_card()
        safe_name = _html_escape(display_name)
        heading = QtWidgets.QLabel(f"<h3>{safe_name}</h3> Scan to pair.")
        heading.setWordWrap(True)
        _apply_property(heading, "role", "heading")

        qr_img = qrcode.make(link).convert("RGB")
        qt_img = ImageQt(qr_img)
        pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(qt_img))
        qr_label = QtWidgets.QLabel(alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        qr_label.setPixmap(
            pixmap.scaled(
                280,
                280,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
        )

        link_field = QtWidgets.QLineEdit(link)
        link_field.setReadOnly(True)

        copy_btn = QtWidgets.QPushButton("Copy link")
        copy_btn.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(link))
        _style_button(copy_btn, "outline")

        card_layout = card.layout()
        card_layout.addWidget(heading)
        card_layout.addWidget(qr_label)
        link_caption = QtWidgets.QLabel("Pairing link")
        _apply_property(link_caption, "variant", "subtle")
        card_layout.addWidget(link_caption)
        card_layout.addWidget(link_field)
        card_layout.addWidget(copy_btn)
        layout.addWidget(card)


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
        self.setFixedSize(840, 560)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setObjectName("MainTabs")
        self.tabs.setIconSize(QtCore.QSize(22, 22))
        self.tabs.setElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.tabs.setDocumentMode(True)

        self.tab_primary = self._build_primary_tab()
        self.tab_stats = self._build_stats_tab()
        self.tab_feedback = self._build_feedback_tab()
        self.tab_support = self._build_support_tab()

        # Load custom tab icons
        track_icon = _load_tab_icon("Track.png")
        stats_icon = _load_tab_icon("stats.png")
        feedback_icon = _load_tab_icon("feedback.png")
        support_icon = _load_tab_icon("support.png")
        
        self.tabs.addTab(self.tab_primary, track_icon, "Tracking")
        self.tabs.addTab(self.tab_stats, stats_icon, "Statistics")
        self.tabs.addTab(self.tab_feedback, feedback_icon, "Feedback")
        self.tabs.addTab(self.tab_support, support_icon, "Support")
        self.tabs.tabBar().setExpanding(True)

        central = QtWidgets.QWidget()
        central.setObjectName("MainSurface")
        central_layout = QtWidgets.QVBoxLayout(central)
        central_layout.setContentsMargins(24, 18, 24, 18)
        central_layout.setSpacing(16)

        hero = self._build_hero()
        central_layout.addWidget(hero)
        central_layout.addWidget(self.tabs)
        self.setCentralWidget(central)

        self.sendResult.connect(self._handle_send_result)
        self.statusMessage.connect(self._show_status)

        # Keyboard shortcuts for toggling tracking
        self.toggle_action = QtGui.QAction("Toggle Tracking", self)
        self.toggle_action.setShortcuts([QtGui.QKeySequence("Ctrl+T"), QtGui.QKeySequence("F8")])
        self.toggle_action.triggered.connect(self._toggle_tracking_shortcut)
        self.addAction(self.toggle_action)

        self.statusBar().showMessage("Ready")
        self._refresh_stats()
        self._update_primary_state()

        # Warmup cache for instant notifications
        try:
            warmup_cache(self.cfg["user_id"])
            self.statusBar().showMessage("Ready - Notification cache warmed up", 3000)
        except Exception:
            self.statusBar().showMessage("Ready", 3000)

        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_stats)
        self.refresh_timer.start(120_000)
        
        # Refresh token cache every 5 minutes to keep it current
        self.cache_refresh_timer = QtCore.QTimer(self)
        self.cache_refresh_timer.timeout.connect(lambda: refresh_token_cache(self.cfg["user_id"]))
        self.cache_refresh_timer.start(300_000)  # 5 minutes

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self._stop_detector()
        super().closeEvent(event)
        
    def _toggle_tracking_shortcut(self) -> None:
        if not self.toggle_button.isEnabled():
            self.statusBar().showMessage("Confirm notifications first", 4000)
            return
        # Simulate a click so existing logic runs
        self.toggle_button.click()

    def _build_hero(self) -> QtWidgets.QWidget:
        frame = QtWidgets.QFrame()
        frame.setObjectName("HeroCard")
        frame.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        layout = QtWidgets.QHBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)

        icon_label = QtWidgets.QLabel()
        icon_label.setFixedSize(60, 60)
        icon_pixmap = APP_ICON.pixmap(56, 56)
        if icon_pixmap.isNull():
            fallback = resource_path("docs/icon-192.png")
            if fallback.exists():
                icon_pixmap = QtGui.QPixmap(str(fallback)).scaled(56, 56, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        if icon_pixmap.isNull():
            icon_pixmap = QtGui.QPixmap(56, 56)
            icon_pixmap.fill(QtGui.QColor("#4caf50"))
        icon_label.setPixmap(icon_pixmap)
        icon_label.setScaledContents(True)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(4)
        text_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)

        title = QtWidgets.QLabel(APP_NAME)
        _apply_property(title, "role", "heroTitle")

        tagline = QtWidgets.QLabel("Accept-button tracker with instant push alerts to your phone.")
        tagline.setWordWrap(True)
        _apply_property(tagline, "variant", "subtle")

        safe_name = _html_escape(self.cfg.get("display_name", "") or "This PC")
        self.device_chip = QtWidgets.QLabel(f"Device: {safe_name}")
        _apply_property(self.device_chip, "role", "pill")

        chip_row = QtWidgets.QHBoxLayout()
        chip_row.setSpacing(10)
        chip_row.addWidget(self.device_chip)
        chip_row.addStretch(1)

        text_layout.addWidget(title)
        text_layout.addWidget(tagline)
        text_layout.addLayout(chip_row)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch(1)
        return frame

    # Primary tab ---------------------------------------------------------
    def _build_primary_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        outer = QtWidgets.QVBoxLayout(w)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(12)

        card = _create_card()
        card_layout = card.layout()
        card_layout.setSpacing(10)

        # Consistent heading style
        heading = QtWidgets.QLabel("Game Tracking")
        _apply_property(heading, "role", "heading")

        safe_name = _html_escape(self.cfg.get("display_name", "") or "founder")
        hello = QtWidgets.QLabel(f"Welcome back, {safe_name}")
        hello.setWordWrap(True)
        _apply_property(hello, "variant", "subtle")

        # Notification status with color coding
        self.notification_state = QtWidgets.QLabel()
        self.notification_state.setWordWrap(True)
        _apply_property(self.notification_state, "variant", "subtle")

        # Action buttons row
        buttons_row = QtWidgets.QHBoxLayout()
        buttons_row.setSpacing(12)

        qr_btn = QtWidgets.QPushButton("Show Pairing QR")
        qr_btn.clicked.connect(self._show_pairing)
        _style_button(qr_btn, "outline")
        qr_btn.setMinimumHeight(40)

        self.test_button = QtWidgets.QPushButton("Send Test")
        self.test_button.clicked.connect(self._send_test_notification)
        _style_button(self.test_button, "outline")
        self.test_button.setMinimumHeight(40)

        self.toggle_button = QtWidgets.QPushButton("OFF")
        self.toggle_button.setObjectName("TrackingToggle")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self._handle_toggle)
        _style_button(self.toggle_button, "toggle")
        self.toggle_button.setMinimumWidth(120)
        self.toggle_button.setMinimumHeight(40)
        self.toggle_button.setToolTip("Toggle tracking (Ctrl+T or F8)")

        buttons_row.addWidget(qr_btn)
        buttons_row.addWidget(self.test_button)
        buttons_row.addWidget(self.toggle_button)
        buttons_row.addStretch(1)

        # Status message
        self.detector_status = QtWidgets.QLabel()
        self.detector_status.setWordWrap(True)
        _apply_property(self.detector_status, "variant", "subtle")

        card_layout.addWidget(heading)
        card_layout.addWidget(hello)
        card_layout.addWidget(self.notification_state)
        card_layout.addLayout(buttons_row)
        card_layout.addWidget(self.detector_status)
        card_layout.addStretch(1)

        self._set_tracking_state(False, "Tracking idle")

        outer.addWidget(card)
        outer.addStretch(1)
        return w

    def _set_tracking_state(self, active: bool, detail: Optional[str] = None) -> None:
        """Update toggle button state and text."""
        with QtCore.QSignalBlocker(self.toggle_button):
            self.toggle_button.setChecked(active)
        self.toggle_button.setText("ON" if active else "OFF")
        
        if detail is not None:
            self.detector_status.setText(detail)

    def _update_primary_state(self) -> None:
        confirmed = bool(self.cfg.get("test_confirmed"))
        if confirmed:
            self.notification_state.setText("✔ Notifications confirmed")
            self.notification_state.setStyleSheet("color: #4caf50;")  # Green
            self.toggle_button.setEnabled(True)
        else:
            self.notification_state.setText("❌ Complete the test notification to unlock tracking.")
            self.notification_state.setStyleSheet("color: #ff6b6b;")  # Red
            self.toggle_button.setEnabled(False)
        active = bool(self.detector and self.detector.isRunning())
        if active:
            self._set_tracking_state(True)
        else:
            detail = "Tracking idle"
            if not confirmed:
                detail = "Tracking locked until notifications are confirmed."
            self._set_tracking_state(False, detail)

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
                self._set_tracking_state(False, "Tracking locked until notifications are confirmed.")
                return
            self._start_detector()
        else:
            self._stop_detector()

    def _start_detector(self) -> None:
        path = _default_template_path()
        if not path.exists():
            self.statusBar().showMessage("Embedded template image missing", 6000)
            self._set_tracking_state(False, "Template image missing. Please reinstall.")
            return
        
        # Hardcoded optimal values
        threshold = 0.7  # Lower threshold for better detection
        debounce_seconds = 4  # 4-second cooldown between notifications (keep alerting user)
        poll_ms = 250

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
            threshold=threshold,
            debounce_seconds=debounce_seconds,
            poll_ms=poll_ms,
            on_match=on_match,
        )
        self.detector.match_detected.connect(self._on_match_detected)
        self.detector.status.connect(self._on_detector_status)
        self.detector.finished.connect(self._on_detector_finished)
        self.detector.start()
        self._set_tracking_state(True, "Detector warming up…")
        self.statusBar().showMessage("Tracking started", 4000)

    @QtCore.pyqtSlot(int, int)
    def _handle_send_result(self, sent: int, total: int) -> None:
        if sent > 0:
            # Detector sends notifications every 4 seconds (keep alerting)
            # But only count as a NEW match if 60+ seconds since last match
            last_ts = self.cfg.get("last_match_ts")
            now = datetime.now(timezone.utc)
            should_increment = True
            
            if last_ts:
                try:
                    last_dt = datetime.fromisoformat(last_ts.replace('Z', '+00:00'))
                    if hasattr(last_dt, 'tzinfo') and last_dt.tzinfo is None:
                        last_dt = last_dt.replace(tzinfo=timezone.utc)
                    time_diff = (now - last_dt).total_seconds()
                    if time_diff < 60:  # Less than 60 seconds = same match
                        should_increment = False
                except (ValueError, AttributeError):
                    pass
            
            if should_increment:
                # NEW match - increment counter
                self.cfg["total_matches"] = int(self.cfg.get("total_matches", 0)) + 1
                self.cfg["last_match_ts"] = now.isoformat()
                save_config(self.cfg)
                self.last_match_label.setText(self._format_last_match())
                self.total_match_label.setText(str(self.cfg["total_matches"]))
                self.statusBar().showMessage(f"Match #{self.cfg['total_matches']}: Notification sent to {sent} device(s)", 4000)
            else:
                # Same match - just re-alert, don't increment counter
                self.statusBar().showMessage(f"Re-alert sent to {sent} device(s) (same match)", 3000)
        else:
            self.statusBar().showMessage("No tokens to send", 6000)

    @QtCore.pyqtSlot(str)
    def _on_detector_status(self, message: str) -> None:
        self._set_tracking_state(True, message)

    @QtCore.pyqtSlot()
    def _on_detector_finished(self) -> None:
        self.detector = None
        self._set_tracking_state(False, "Tracking idle")
        self.statusBar().showMessage("Tracking stopped", 4000)

    @QtCore.pyqtSlot(float)
    def _on_match_detected(self, score: float) -> None:
        self._set_tracking_state(True, "Match detected! Sending notification...")

    @QtCore.pyqtSlot(str)
    def _show_status(self, message: str) -> None:
        self.statusBar().showMessage(message, 6000)

    def _stop_detector(self) -> None:
        was_running = bool(self.detector and self.detector.isRunning())
        if self.detector and self.detector.isRunning():
            self.detector.stop()
            self.detector.wait(2000)
        self.detector = None
        self._set_tracking_state(False, "Tracking idle")
        if was_running:
            self.statusBar().showMessage("Tracking stopped", 4000)

    def _show_pairing(self) -> None:
        dlg = PairingDialog(self.cfg.get("display_name", ""), self.cfg.get("pairing_link", PWA_URL), self)
        dlg.exec()

    def _format_last_match(self) -> str:
        ts = self.cfg.get("last_match_ts")
        if not ts:
            return "Never"
        try:
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            # Handle legacy timestamps without timezone
            if hasattr(dt, 'tzinfo') and dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return ts
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    # Stats tab -----------------------------------------------------------
    def _build_stats_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        outer = QtWidgets.QVBoxLayout(w)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(10)

        card = _create_card()
        card_layout = card.layout()
        card_layout.setSpacing(10)

        # Your Activity Section (Personal Stats First)
        activity_heading = QtWidgets.QLabel("Your Activity")
        activity_heading.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 15px;
            font-weight: 650;
            color: #e7ecf3;
            letter-spacing: 0.3px;
            margin-top: 6px;
        """)

        # Personal stats - only Games Found and Last Match
        self.total_match_label = QtWidgets.QLabel(str(self.cfg.get("total_matches", 0)))
        self.total_match_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: #4caf50;
        """)
        self.total_match_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        total_match_box = self._make_compact_stat_box(self.total_match_label, "Games Found")

        last_match_text = self._format_last_match()
        if last_match_text == "Never":
            last_match_text = "------------"
        
        self.last_match_label = QtWidgets.QLabel(last_match_text)
        self.last_match_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            font-weight: 700;
            color: #a9b3c7;
        """)
        self.last_match_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.last_match_label.setWordWrap(True)
        last_match_box = self._make_compact_stat_box(self.last_match_label, "Last Match")

        personal_row = QtWidgets.QHBoxLayout()
        personal_row.setSpacing(10)
        personal_row.addWidget(total_match_box)
        personal_row.addWidget(last_match_box)

        card_layout.addWidget(activity_heading)
        card_layout.addLayout(personal_row)

        # Separator line
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setStyleSheet("background: rgba(255, 255, 255, 0.12); max-height: 1px; margin: 6px 0px;")
        card_layout.addWidget(separator)

        # Community Stats Section with header row
        header_row = QtWidgets.QHBoxLayout()
        header_row.setSpacing(10)
        
        community_heading = QtWidgets.QLabel("Community Stats")
        community_heading.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 15px;
            font-weight: 650;
            color: #e7ecf3;
            letter-spacing: 0.3px;
            margin-top: 6px;
        """)
        
        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_stats)
        _style_button(refresh_btn, "outline")
        refresh_btn.setMaximumWidth(100)
        refresh_btn.setMaximumHeight(32)
        
        header_row.addWidget(community_heading)
        header_row.addStretch(1)
        header_row.addWidget(refresh_btn)

        self.global_users = QtWidgets.QLabel("0")
        self.global_users.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            font-weight: 700;
            color: #ff6b6b;
        """)
        self.global_users.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        users_box = self._make_compact_stat_box(self.global_users, "Total Users")

        self.global_matches = QtWidgets.QLabel("0")
        self.global_matches.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            font-weight: 700;
            color: #4caf50;
        """)
        self.global_matches.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        matches_box = self._make_compact_stat_box(self.global_matches, "Total Matches")

        self.global_notifications = QtWidgets.QLabel("0")
        self.global_notifications.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            font-weight: 700;
            color: #2196F3;
        """)
        self.global_notifications.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        notifications_box = self._make_compact_stat_box(self.global_notifications, "Total Notifications Sent")

        stats_row = QtWidgets.QHBoxLayout()
        stats_row.setSpacing(10)
        stats_row.addWidget(users_box)
        stats_row.addWidget(matches_box)
        stats_row.addWidget(notifications_box)

        card_layout.addLayout(header_row)
        card_layout.addLayout(stats_row)

        outer.addWidget(card)
        outer.addStretch(1)
        return w

    def _make_compact_stat_box(self, value_label: QtWidgets.QLabel, caption: str) -> QtWidgets.QFrame:
        """Create a compact stat box that fits in the 840px window."""
        box = QtWidgets.QFrame()
        box.setObjectName("StatBox")
        box.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        layout = QtWidgets.QVBoxLayout(box)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(8)
        
        value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        caption_label = QtWidgets.QLabel(caption)
        caption_label.setWordWrap(True)
        caption_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        caption_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #a9b3c7;
            letter-spacing: 0.3px;
        """)
        layout.addWidget(caption_label)
        
        return box

    def _refresh_stats(self) -> None:
        try:
            # fetch_stats now requires user_id and returns (PersonalStats, GlobalStats)
            personal, global_stats = fetch_stats(self.cfg["user_id"])
        except Exception as exc:
            self.statusBar().showMessage(f"Stats unavailable: {exc}", 6000)
            return
        self._apply_stats(personal, global_stats)

    def _apply_stats(self, personal, global_stats: GlobalStats) -> None:
        # Update personal stats
        self.total_match_label.setText(str(personal.matches_found))
        
        # Also update local config to stay in sync
        self.cfg["total_matches"] = personal.matches_found
        save_config(self.cfg)
        
        # Update last match timestamp display
        self.last_match_label.setText(self._format_last_match())
        
        # Update global stats  
        self.global_users.setText(str(global_stats.total_users))
        self.global_matches.setText(str(global_stats.total_matches))
        self.global_notifications.setText(str(global_stats.total_notifications))

    # Feedback tab --------------------------------------------------------
    def _build_feedback_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        outer = QtWidgets.QVBoxLayout(w)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(10)

        card = _create_card()
        card_layout = card.layout()
        card_layout.setSpacing(10)

        heading = QtWidgets.QLabel("Feedback")
        _apply_property(heading, "role", "heading")

        helper = QtWidgets.QLabel("Share your ideas, report bugs, or tell us about your wins—your feedback goes straight to the creator.")
        helper.setWordWrap(True)
        _apply_property(helper, "variant", "subtle")

        self.feedback_edit = QtWidgets.QPlainTextEdit()
        self.feedback_edit.setPlaceholderText("Tell us what to improve or report issues…")
        self.feedback_edit.textChanged.connect(self._update_feedback_counter)

        self.feedback_status = QtWidgets.QLabel()
        _apply_property(self.feedback_status, "variant", "subtle")
        
        # Word counter at far left, submit button at far right on same line at the bottom
        bottom_row = QtWidgets.QHBoxLayout()
        bottom_row.setSpacing(16)
        
        self.feedback_counter = QtWidgets.QLabel(f"0 / {FEEDBACK_WORD_LIMIT} words")
        _apply_property(self.feedback_counter, "variant", "subtle")

        submit_btn = QtWidgets.QPushButton("Submit Feedback")
        submit_btn.clicked.connect(self._submit_feedback)
        _style_button(submit_btn, "primary")
        submit_btn.setMinimumWidth(150)

        bottom_row.addWidget(self.feedback_counter)
        bottom_row.addStretch(1)
        bottom_row.addWidget(submit_btn)

        card_layout.addWidget(heading)
        card_layout.addWidget(helper)
        card_layout.addWidget(self.feedback_status)
        card_layout.addWidget(self.feedback_edit, 1)  # stretch=1 to fill available space
        card_layout.addLayout(bottom_row)

        outer.addWidget(card)
        outer.addStretch(1)
        self._update_feedback_counter()
        return w

    def _submit_feedback(self) -> None:
        text = self.feedback_edit.toPlainText().strip()
        words = _word_count(text)
        if not text:
            self.feedback_status.setText("Enter some feedback first.")
            _apply_property(self.feedback_status, "variant", "danger")
            return
        if words > FEEDBACK_WORD_LIMIT:
            self.feedback_status.setText(f"Feedback is limited to {FEEDBACK_WORD_LIMIT} words. Please shorten it.")
            _apply_property(self.feedback_status, "variant", "danger")
            return
        try:
            submit_feedback(self.cfg["user_id"], self.cfg.get("display_name", ""), text)
        except Exception as exc:
            self.feedback_status.setText(f"Failed to submit: {exc}")
            _apply_property(self.feedback_status, "variant", "danger")
            return
        self.feedback_edit.clear()
        self.feedback_status.setText("Thanks! Feedback sent.")
        _apply_property(self.feedback_status, "variant", "success")
        
        # Show thank you message with custom icon
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Feedback sent")
        msg_box.setText("Thanks for sharing your feedback with OmniCall!")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        
        # Try to load thanks.png icon
        thanks_icon = _load_tab_icon("thanks.png")
        if not thanks_icon.isNull():
            msg_box.setIconPixmap(thanks_icon.pixmap(64, 64))
        else:
            msg_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        
        msg_box.exec()
        self._update_feedback_counter()

    def _update_feedback_counter(self) -> None:
        words = _word_count(self.feedback_edit.toPlainText())
        self.feedback_counter.setText(f"{words} / {FEEDBACK_WORD_LIMIT} words")
        variant = "danger" if words > FEEDBACK_WORD_LIMIT else "subtle"
        _apply_property(self.feedback_counter, "variant", variant)
        if not words and self.feedback_status.text():
            self.feedback_status.clear()
            _apply_property(self.feedback_status, "variant", "subtle")

    # Support tab --------------------------------------------------------
    def _build_support_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        outer = QtWidgets.QVBoxLayout(w)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(10)

        card = _create_card()
        card_layout = card.layout()
        card_layout.setSpacing(10)

        heading = QtWidgets.QLabel("Support")
        _apply_property(heading, "role", "heading")

        helper = QtWidgets.QLabel("If OmniCall helps you, consider supporting the creator. Every contribution keeps the upgrades coming. Thank you! ❤️")
        helper.setWordWrap(True)
        _apply_property(helper, "variant", "subtle")

        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(16)
        content_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        art_label = QtWidgets.QLabel()
        art_label.setObjectName("SupportArt")
        art_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        art_label.setMinimumSize(180, 170)
        art_label.setMaximumSize(180, 170)
        art_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)

        art_pixmap = QtGui.QPixmap()
        for rel in ("support_page.jpeg", "pc_app/support_page.jpeg", "../pc_app/support_page.jpeg", "docs/support_page.jpeg"):
            path = resource_path(rel)
            if path.exists():
                art_pixmap = QtGui.QPixmap(str(path))
                break
        if art_pixmap.isNull():
            art_pixmap = QtGui.QPixmap(180, 170)
            art_pixmap.fill(QtGui.QColor("#4caf50"))
        art_label.setPixmap(
            art_pixmap.scaled(
                180,
                170,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
        )

        binance_detail = (
            'Email: <a href="mailto:amrkhaled272@gmail.com">amrkhaled272@gmail.com</a><br/>'
            "ID: <strong>753805136</strong>"
        )
        paypal_detail = 'Email: <a href="mailto:amrkhaled122@aucegypt.edu">amrkhaled122@aucegypt.edu</a>'

        binance_item = _make_support_item("Binance", binance_detail, "#f59e0b", "B", "binance.png")
        paypal_item = _make_support_item("PayPal", paypal_detail, "#2563eb", "P", "paypal.png")

        footnote = QtWidgets.QLabel("Please copy carefully when sending. Much appreciated!")
        footnote.setWordWrap(True)
        _apply_property(footnote, "variant", "subtle")

        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setSpacing(12)
        info_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        info_layout.addWidget(binance_item)
        info_layout.addWidget(paypal_item)
        info_layout.addSpacing(8)
        info_layout.addWidget(footnote)
        info_layout.addStretch(1)

        content_layout.addWidget(art_label)
        content_layout.addSpacing(16)
        content_layout.addLayout(info_layout, stretch=1)

        card_layout.addWidget(heading)
        card_layout.addWidget(helper)
        card_layout.addLayout(content_layout)

        outer.addWidget(card)
        outer.addStretch(1)
        return w


def _default_template_path() -> Path:
    for candidate in ("../Accept.png", "Accept.png"):
        path = resource_path(candidate)
        if path.exists():
            return path
    return Path.home()


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    if hasattr(QtCore.Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        app.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    app.setStyle("Fusion")
    app.setFont(QtGui.QFont(FONT_FAMILY, 10))
    app.setStyleSheet(APP_STYLE)

    palette = app.palette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#0f1115"))
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor("#141822"))
    palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor("#1b2130"))
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#1b2130"))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor("#e7ecf3"))
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("#e7ecf3"))
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor("#4caf50"))
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor("#0f1115"))
    app.setPalette(palette)

    QtWidgets.QApplication.setApplicationName(APP_NAME)
    global APP_ICON
    APP_ICON = _load_app_icon()
    if not APP_ICON.isNull():
        app.setWindowIcon(APP_ICON)

    cfg = load_config()
    cfg.pop("template_path", None)
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
