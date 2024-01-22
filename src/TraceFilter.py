from typing import Any, Self

from FilterDSL import FilterDSL
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
        self.filter: FilterDSL | None = None
        self.format: str = "[{timestamp}][{module:10}] : {message}"
        self.setSourceModel(model)
        self.setDynamicSortFilter(False)
        model.global_time_updated.connect(self.global_time_updated)

    def data(self: Self, index: QModelIndex, role: Qt.ItemDataRole | None = None) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            item : TraceMessage = super().data(index, Qt.ItemDataRole.UserRole)
            try:
                return self.format.format_map(item)
            except ValueError as e:
                return str(e)
        return super().data(index, role)

    def sourceModel(self: Self) -> TraceModel:  # noqa: N802
        model = super().sourceModel()
        if not isinstance(model, TraceModel):
            raise TypeError("TraceFilter does not contain TraceModel as model")
        return model

    def filterAcceptsRow(self: Self, source_row: int,  # noqa: N802
                         source_parent: QModelIndex | QPersistentModelIndex) -> bool:
        if source_row >= len(self.sourceModel().logs):
            return False

        if self.filter is None:
            return True

        log = self.sourceModel().logs[source_row]
        return self.filter.eval(log.__dict__)

    def update_filter(self: Self, new_filter: str) -> None:
        new_model = None
        if new_filter.strip() != "":
            new_model = FilterDSL(new_filter)
            new_model.eval(self.sourceModel().logs[0].__dict__)
        self.beginResetModel()
        self.filter = new_model
        self.endResetModel()

    def update_format(self: Self, new_format:str) -> None:
        self.format = new_format

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
            potential_match : TraceMessage = self.data(self.index(middle, 0), role = Qt.ItemDataRole.UserRole)
            if timestamp == potential_match.timestamp:
                break
            elif timestamp < potential_match.timestamp:
                right = middle - 1
            else:
                left = middle + 1
        if right < 0:
            right = 0
        guess : TraceMessage = self.data(self.index(right, 0), role = Qt.ItemDataRole.UserRole)
        if guess is not None:
            self.view_scroll_to_index.emit(self.index(right, 0))
