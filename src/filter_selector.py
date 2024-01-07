from typing import Self

import qtawesome as qta
from PySide6.QtCore import QSize, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class FilterWidget(QWidget):
    filter_updated = Signal(list)

    def __init__(self: Self, filter_items: list[int], name: str) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # Search bar
        self.search_bar_widget = QLineEdit()
        self.search_bar_widget.setPlaceholderText(f"Search for {name}")
        self.search_bar_widget.textChanged.connect(self.filter_list)
        self.layout.addWidget(self.search_bar_widget)

        # List
        self.item_list_widget = QListWidget()
        self.item_list_widget.itemClicked.connect(self.toggle_item)
        self.layout.addWidget(self.item_list_widget)

        # Populate list widget
        self.filter_items: dict[str, bool] = {}
        for i in filter_items:
            self.filter_items[i] = True
            self.item_list_widget.addItem(QListWidgetItem(i))

        # Buttons
        self.btn_select_all = QPushButton("Select all")
        self.btn_deselect_all = QPushButton("Deselect all")
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.btn_select_all)
        self.btn_layout.addWidget(self.btn_deselect_all)

        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_deselect_all.clicked.connect(self.deselect_all)
        self.layout.addLayout(self.btn_layout)

        self.update_items()

    def sizeHint(self: Self) -> QSize:  # noqa: N802
        return QSize(300, 300)

    @Slot(str)
    def filter_list(self: Self, search: str) -> None:
        for i in range(0, self.item_list_widget.count()):
            item = self.item_list_widget.item(i)
            item.setHidden(search not in item.text())

    @Slot(bool)
    def select_all(self: Self, checked: bool) -> None:
        for i in self.filter_items:
            self.filter_items[i] = True
        self.update_items()

    @Slot(bool)
    def deselect_all(self: Self, checked: bool) -> None:
        for i in self.filter_items:
            self.filter_items[i] = False
        self.update_items()

    @Slot(QListWidgetItem)
    def toggle_item(self: Self, item: QListWidgetItem) -> None:
        self.filter_items[item.text()] = not self.filter_items[item.text()]
        self.update_items()

    def update_items(self: Self) -> None:
        for i in range(0, self.item_list_widget.count()):
            item = self.item_list_widget.item(i)
            if self.filter_items[item.text()]:
                icon = qta.icon("fa5.check-circle")
            else:
                icon = qta.icon("fa5.circle")
            item.setIcon(icon)
        self.send_update_signal()

    def send_update_signal(self: Self) -> None:
        items_in_filter = []
        for item, selected in self.filter_items.items():
            if selected:
                items_in_filter.append(item)

        self.filter_updated.emit(items_in_filter)
