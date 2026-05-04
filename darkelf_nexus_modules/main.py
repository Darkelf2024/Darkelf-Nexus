# main.py

# --- Qt ---
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

# --- Standard ---
import sys

# --- Local modules ---
from nexus.splash import BootSplash
from nexus.boot import BootWorker, update_progress, boot_done

# --- Chromium flags MUST be before Qt ---
from nexus.utils import apply_chromium_flags
apply_chromium_flags()

import sys

# --- Create app ---
app = QApplication(sys.argv)

# 🔥 CRITICAL: prevent app from quitting when splash closes
app.setQuitOnLastWindowClosed(False)

# 🔥 CRITICAL: FORCE CONSISTENT STYLE ENGINE
app.setStyle("Fusion")

# 🔥 GLOBAL DARK THEME (this is what your monolith had implicitly)
palette = QPalette()

palette.setColor(QPalette.Window, QColor("#0d0f12"))
palette.setColor(QPalette.Base, QColor("#0d0f12"))
palette.setColor(QPalette.AlternateBase, QColor("#0d0f12"))

palette.setColor(QPalette.Text, QColor("#00FF9C"))
palette.setColor(QPalette.ButtonText, QColor("#00FF9C"))

palette.setColor(QPalette.Button, QColor("#0d0f12"))

palette.setColor(QPalette.Highlight, QColor("#00FF9C"))
palette.setColor(QPalette.HighlightedText, QColor("#000000"))

app.setPalette(palette)

# 🔥 OPTIONAL: Global stylesheet (stabilizes tabs + toolbar rendering)
app.setStyleSheet("""
QTabWidget::pane {
    border: none;
}

QTabBar::tab {
    background: #0d0f12;
    color: #00FF9C;
    padding: 6px 14px;
    border-radius: 8px;
    margin: 2px;
}

QTabBar::tab:selected {
    background: #00FF9C;
    color: #000000;
}

QToolBar {
    background: #0d0f12;
    border: none;
}

QToolButton {
    color: #00FF9C;
    padding: 6px;
}

QToolButton:hover {
    background: #003322;
}
""")

# --- Splash screen ---
splash = BootSplash()
splash.show()

# --- Boot worker ---
worker = BootWorker()

# --- Connect progress updates ---
worker.progress.connect(lambda v, t: update_progress(splash, v, t))

# --- Connect completion ---
worker.finished.connect(
    lambda engine, ai: boot_done(splash, app, engine, ai)
)

# --- Start boot process ---
worker.start()

# --- Run app ---
sys.exit(app.exec())
