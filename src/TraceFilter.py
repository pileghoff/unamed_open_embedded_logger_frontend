from typing import Self

from loguru import logger
from PySide6.QtCore import (
    QModelIndex,
    QPersistentModelIndex,
    QSortFilterProxyModel,
    Qt,
    Signal,
    Slot,
)
from TraceModel import TraceMessage, TraceModel


class TraceFilter(QSortFilterProxyModel):
    view_scroll_to_index = Signal(QModelIndex)

    def __init__(self: Self, model: TraceModel) -> None:
        super(TraceFilter, self).__init__()
        self.task_ids: set[str] = set()
        self.modules: set[str] = set()
        self.setSourceModel(model)
        model.global_time_updated.connect(self.global_time_updated)

    def sourceModel(self: Self) -> TraceModel:  # noqa: N802
        model = super().sourceModel()
        if not isinstance(model, TraceModel):
            raise TypeError("TraceFilter does not contain TraceModel as model")
        return model

    def filterAcceptsRow(self: Self, source_row: int,  # noqa: N802
                         source_parent: QModelIndex | QPersistentModelIndex) -> bool:
        if source_row >= len(self.sourceModel().logs):
            return False
        log = self.sourceModel().logs[source_row]
        return log.task_id in self.task_ids and log.module in self.modules

    @Slot(list)
    def update_modules(self: Self, modules: list[str]) -> None:
        self.beginResetModel()
        self.modules = set(modules)
        self.endResetModel()

    @Slot(list)
    def update_tasks(self: Self, tasks: list[str]) -> None:
        self.beginResetModel()
        self.task_ids = set(tasks)
        self.endResetModel()

    @Slot(QModelIndex)
    def scrolled_to_index(self: Self, index: QModelIndex) -> None:
        source_index: QModelIndex = self.mapToSource(index)
        self.sourceModel().set_active(source_index)

    @Slot(int)
    def global_time_updated(self: Self, timestamp: int) -> None:
        left = 0
        right = self.rowCount() - 1
        while left <= right:
            middle = (left+right) // 2
            logger.warning(f"Attempt lookup at {middle}")
            potentialMatch : TraceMessage = self.data(self.index(middle, 0), role = Qt.ItemDataRole.UserRole)
            if timestamp == potentialMatch.timestamp:
                break
            elif timestamp < potentialMatch.timestamp:
                right = middle - 1
            else:
                left = middle + 1
        guess : TraceMessage = self.data(self.index(left, 0), role = Qt.ItemDataRole.UserRole)
        logger.warning(f"Scroll to: {guess.timestamp}")
        self.view_scroll_to_index.emit(self.index(left, 0))







# How to do this as a binary search
# We have a row count
