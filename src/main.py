import sys
import traceback
from typing import Self

import qtawesome as qta
from loguru import logger
from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from TabContainer import TabContainer, TabWidget
from TraceWidget import TraceTab, TraceWidget


class MainWindow(QMainWindow):
    def __init__(self: Self) -> None:
        super().__init__()
        self.trace_tab = TraceTab()
        self.setCentralWidget(self.trace_tab)
        self.toolbar = self.addToolBar("Test")

        connect_action = QAction(qta.icon("fa5s.plug"), "Setup connection", self)
        connect_action.triggered.connect(self.open_connect_dialog)
        self.toolbar.addAction(connect_action)

        start_stream_action = QAction(qta.icon("fa5s.play"), "Start connection", self)
        start_stream_action.triggered.connect(self.start_stream)
        self.toolbar.addAction(start_stream_action)

        pause_stream_action = QAction(qta.icon("fa5s.pause"), "Stop connection", self)
        pause_stream_action.triggered.connect(self.pause_stream)
        self.toolbar.addAction(pause_stream_action)

        clear_log_action = QAction(qta.icon("fa5s.trash"), "Clear log", self)
        clear_log_action.triggered.connect(self.clear_log)
        self.toolbar.addAction(clear_log_action)

        add_tab_action = QAction(qta.icon("fa5s.columns"), "New tab", self)
        add_tab_action.triggered.connect(self.add_tab)
        self.toolbar.addAction(add_tab_action)

        settings_action = QAction(qta.icon("fa5s.cogs"), "Settings", self)
        settings_action.triggered.connect(self.open_settings)
        self.toolbar.addAction(settings_action)

        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolbar.setIconSize(QSize(150, 25))

        self.toolbar.setMovable(False)

    @Slot(bool)
    def open_connect_dialog(self: Self) -> None:
        logger.info("open_connect_dialog")

    @Slot(bool)
    def start_stream(self: Self) -> None:
        self.trace_tab.trace_tab_model.start_stream()

    @Slot(bool)
    def pause_stream(self: Self) -> None:
        self.trace_tab.trace_tab_model.pause_stream()

    @Slot(bool)
    def clear_log(self: Self) -> None:
        self.trace_tab.trace_tab_model.clear()

    @Slot(bool)
    def add_tab(self: Self) -> None:
        self.trace_tab.addTab()

    @Slot(bool)
    def open_settings(self: Self) -> None:
        logger.info("Open settings")

    @Slot(bool)
    def focus_changed(self: Self, old: QWidget, new: QWidget) -> None:
        # Set the active child of the draggable split
        if new is None:
            return
        w = new

        child_tab = None
        while not isinstance(w, MainWindow):
            logger.info(type(w))
            if isinstance(w, TraceWidget):
                self.trace_tab.set_active_child(w)
            if isinstance(w, TabWidget):
                child_tab = w
            if isinstance(w, TabContainer):
                if child_tab is not None:
                    w.set_active_child(child_tab)

            w = w.parentWidget()


def excepthook(cls, exception, tb):
    logger.error(f"Exception: {exception}")
    for l in traceback.format_exception(exception):
        logger.error(l.strip("\n"))
    exit(-1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    app.focusChanged.connect(window.focus_changed)
    sys.excepthook = excepthook
    app.exec()
