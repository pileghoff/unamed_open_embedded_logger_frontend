from typing import Self

from FilterDSL import UnknownIdent
from lark.exceptions import UnexpectedInput
from loguru import logger
from PySide6.QtCore import (
    QAbstractItemModel,
    QItemSelection,
    QModelIndex,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from TabContainer import TabContainer
from TraceFilter import TraceFilter
from TraceModel import TraceModel


class TraceListWidget(QListView):
    toggle_search_bar = Signal()

    def __init__(self: Self, model:QAbstractItemModel) -> None:
        super().__init__()
        self.setModel(model)

        self.setUniformItemSizes(True)

        self.verticalScrollBar().valueChanged.connect(self.user_scroll)
        model.rowsInserted.connect(self.scroll_update)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setStyleSheet("font-family: monospace;")
        self.scroll_follow = True

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
        self.scroll_follow = slider_value == scroll_bar.maximum()

    def selectionChanged(self: Self, selected: QItemSelection, deselected: QItemSelection) -> None:
        super().selectionChanged(selected, deselected)

        if len(selected) > 0:
            i:QModelIndex = selected[0].indexes()[0]
            self.model().scrolled_to_index(i)

    @Slot(QModelIndex, int, int)
    def scroll_update(self, parent: QModelIndex, first:int, last:int) -> None:
        if self.scroll_follow:
            self.scrollToBottom()


class TraceWidget(QWidget):
    def __init__(self: Self, model: QAbstractItemModel) -> None:
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.trace_model = model
        self.trace_filtered_model = TraceFilter(model)
        self.trace_filtered_model.view_scroll_to_index.connect(self.scoll_to_item)

        self.setMouseTracking(True)

        # Top
        self.top = QWidget()
        self.top.setLayout(QHBoxLayout())
        self.layout().addWidget(self.top)

        # Filter widget
        self.filter_input_widget_container = QWidget()
        self.filter_input_widget_container.setLayout(QVBoxLayout())
        self.filter_input_widget = QLineEdit()
        self.filter_input_widget.editingFinished.connect(self.update_filter)
        self.filter_error_message = QLabel()
        self.filter_input_widget_container.layout().addWidget(self.filter_input_widget)
        self.filter_input_widget_container.layout().addWidget(self.filter_error_message)
        self.top.layout().addWidget(self.filter_input_widget_container)

        # Format widget
        self.format_input_widget = QLineEdit()
        self.format_input_widget.setText(self.trace_filtered_model.format)
        self.format_input_widget.editingFinished.connect(self.update_format)
        self.top.layout().addWidget(self.format_input_widget)

        # Build log
        self.log_view_widget = TraceListWidget(self.trace_filtered_model)

        self.layout().addWidget(self.log_view_widget, stretch=2)

    @Slot()
    def update_format(self: Self) -> None:
        self.trace_filtered_model.update_format(self.format_input_widget.text())

    @Slot()
    def update_filter(self: Self) -> None:
        self.filter_error_message.setText("")
        try:
            self.trace_filtered_model.update_filter(self.filter_input_widget.text())
        except UnexpectedInput as e:
            self.filter_error_message.setText(e.get_context(self.filter_input_widget.text()))
        except UnknownIdent as e:
            self.filter_error_message.setText(f"Unknown identifier {e.ident}")


    @Slot(QModelIndex)
    def scoll_to_item(self: Self, index: QModelIndex) -> None:
        if not self.underMouse():
            self.log_view_widget.scrollTo(index, hint = QAbstractItemView.ScrollHint.PositionAtCenter)
            self.log_view_widget.setCurrentIndex(index)



class TraceTab(QWidget):
    def __init__(self: Self) -> None:
        super().__init__()
        self.trace_model = TraceModel()
        self.setLayout(QHBoxLayout())
        self.tab_widget = TabContainer()
        self.layout().addWidget(self.tab_widget)
        self.tab_widget.addTab( TraceWidget(self.trace_model), "Tab")


    def addTab(self: Self) -> None:  # noqa: N802
        logger.info("Add new tab")
        self.tab_widget.addTab(TraceWidget(self.trace_model), "New tab")


