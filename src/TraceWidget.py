from typing import Self

import qtawesome as qta
from filter_selector import FilterWidget
from loguru import logger
from PySide6.QtCore import (
    QAbstractItemModel,
    QMargins,
    QModelIndex,
    QObject,
    Qt,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtGui import QCursor, QKeyEvent, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QListView,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from TabContainer import TabContainer
from TraceFilter import TraceFilter
from TraceModel import TraceModel
from utils import has_focus


class TraceListWidget(QListView):
    toggle_search_bar = Signal()

    def __init__(self: Self, model:QAbstractItemModel) -> None:
        super().__init__()
        self.setModel(model)

        self.scroll_follow = True
        self.setUniformItemSizes(True)

        self.verticalScrollBar().valueChanged.connect(self.user_scroll)
        model.rowsInserted.connect(self.scroll_update)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setStyleSheet("font-family: monospace;")

    def keyPressEvent(self: Self, event: QKeyEvent) -> None:  # noqa: N802
        super().keyPressEvent(event)

        if event.matches(QKeySequence.StandardKey.Copy):
            model = self.model()
            lines = [
                model.data(i, Qt.ItemDataRole.DisplayRole)
                for i in self.selectedIndexes()
            ]
            QApplication.clipboard().clear()
            QApplication.clipboard().setText("\n".join(lines))
        if event.matches(QKeySequence.StandardKey.Find):
            self.toggle_search_bar.emit()

    @Slot(int)
    def user_scroll(self: Self, slider_value: int) -> None:
        scroll_bar = self.verticalScrollBar()
        self.model().sourceModel().scroll_follow = slider_value == scroll_bar.maximum()

        if not self.model().sourceModel().scroll_follow and self.parentWidget().underMouse():
            self.model().scrolled_to_index(self.indexAt(self.geometry().center()))


    @Slot(QModelIndex, int, int)
    def scroll_update(self: Self, parent: QObject | None, start: int, end: int) -> None:
        if self.model().sourceModel().scroll_follow:
            self.scrollToBottom()


class TraceWidget(QWidget):
    def __init__(self: Self, model: QAbstractItemModel) -> None:
        super().__init__()
        self.setLayout(QHBoxLayout())
        self.trace_model = model
        self.trace_filtered_model = TraceFilter(model)
        self.trace_filtered_model.view_scroll_to_index.connect(self.scoll_to_item)

        self.setMouseTracking(True)

        # Side bar
        self.side_bar_hidden = qta.IconWidget("fa5s.list")
        self.side_bar = QWidget()
        self.side_bar.setLayout(QVBoxLayout())

        # Module filter widget
        self.module_filter_widget = FilterWidget(self.trace_model.modules, "Modules")
        self.module_filter_widget.filter_updated.connect(
            self.trace_filtered_model.update_modules
        )
        self.module_filter_widget.update_items()
        self.side_bar.layout().addWidget(self.module_filter_widget)

        # Task filter widget
        self.task_filter_widget = FilterWidget([str(i) for i in range(2, 5)], "Tasks")
        self.task_filter_widget.filter_updated.connect(
            self.trace_filtered_model.update_tasks
        )
        self.task_filter_widget.update_items()
        self.side_bar.layout().addWidget(self.task_filter_widget)

        # Build log
        self.log_view_widget = TraceListWidget(self.trace_filtered_model)

        self.layout().addWidget(self.log_view_widget, stretch=2)
        self.layout().addWidget(self.side_bar)
        self.layout().addWidget(self.side_bar_hidden)
        self.hide_sidebar()

        check_hover_timer = QTimer(self)
        check_hover_timer.timeout.connect(self.check_mouse)
        check_hover_timer.start(100)

    def show_sidebar(self: Self) -> None:
        self.side_bar_hidden.setVisible(False)
        self.side_bar.setVisible(True)

    def hide_sidebar(self: Self) -> None:
        restore_focus = has_focus(self)
        self.side_bar.setVisible(False)
        self.side_bar_hidden.setVisible(True)
        if restore_focus:
            self.setFocus()

    @Slot(QModelIndex)
    def scoll_to_item(self: Self, index: QModelIndex) -> None:
        if not self.underMouse():
            self.log_view_widget.scrollTo(index, hint = QAbstractItemView.ScrollHint.PositionAtCenter)

    @Slot()
    def check_mouse(self: Self) -> None:
        cursor = QCursor()
        pos = self.mapFromGlobal(cursor.pos())
        if self.side_bar.isVisible():
            rect = self.side_bar.geometry() + QMargins(20, 0, 10, 0)
            if not rect.contains(pos):
                self.hide_sidebar()
        else:
            if (
                pos - self.side_bar_hidden.geometry().center()
            ).manhattanLength() < self.side_bar_hidden.geometry().width():
                self.show_sidebar()



class TraceTab(QWidget):
    def __init__(self: Self) -> None:
        super().__init__()
        self.trace_model = TraceModel()
        self.setLayout(QHBoxLayout())
        self.tab_widget = TabContainer()
        self.layout().addWidget(self.tab_widget)

        self.active_child = TraceWidget(self.trace_model)
        self.tab_widget.addTab(self.active_child, "Tab")


    def addTab(self: Self) -> None:  # noqa: N802
        logger.info("Add new tab")
        self.active_child = TraceWidget(self.trace_model)
        self.tab_widget.addTab(self.active_child, "New tab")

    def set_active_child(self: Self, child: TraceWidget) -> None:
        if child == self.active_child:
            # do nothing
            return

        self.active_child = child

