from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFontDialog,
    QVBoxLayout,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        # Create widgets for font customization
        self.font_button = self.create_button("Choose Font...", self.change_font)
        self.font_label = self.create_label("Font")
        self.font_size_spinbox = self.create_spinbox(6, 72, 1, self.change_font_size)
        self.font_color_button = self.create_button(
            "Choose Color...", self.change_font_color
        )
        self.font_color_label = self.create_label("Color")

        # Create widgets for background color customization
        self.background_color_button = self.create_button(
            "Choose Color...", self.change_background_color
        )
        self.background_color_label = self.create_label("Background Color")

        # Create widgets for log history length
        self.log_history_spinbox = self.create_spinbox(1, 1000, 10)
        self.log_history_label = self.create_label("Log History Length")

        # Create widgets for buffering time
        self.buffering_time_spinbox = self.create_double_spinbox(0.0, 10.0, 0.1, 1.0)
        self.buffering_time_label = self.create_label("Buffering Time (s)")

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.font_label)
        layout.addWidget(self.font_button)
        layout.addWidget(self.font_size_spinbox)
        layout.addWidget(self.font_color_label)
        layout.addWidget(self.font_color_button)
        layout.addWidget(self.background_color_label)
        layout.addWidget(self.background_color_button)
        layout.addWidget(self.log_history_label)
        layout.addWidget(self.log_history_spinbox)
        layout.addWidget(self.buffering_time_label)
        layout.addWidget(self.buffering_time_spinbox)

        # Add standard OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def create_label(self, text):
        label = self.create_widget("QLabel")
        label.setText(text)
        return label

    def create_button(self, text, slot):
        button = self.create_widget("QPushButton")
        button.setText(text)
        button.clicked.connect(slot)
        return button

    def create_spinbox(self, minimum, maximum, single_step, slot=None):
        spinbox = self.create_widget("QSpinBox")
        spinbox.setMinimum(minimum)
        spinbox.setMaximum(maximum)
        spinbox.setSingleStep(single_step)
        if slot is not None:
            spinbox.valueChanged.connect(slot)
        return spinbox

    def create_double_spinbox(self, minimum, maximum, single_step, value, slot=None):
        spinbox = self.create_widget("QDoubleSpinBox")
        spinbox.setMinimum(minimum)
        spinbox.setMaximum(maximum)
        spinbox.setSingleStep(single_step)
        spinbox.setValue(value)
        if slot is not None:
            spinbox.valueChanged.connect(slot)
        return spinbox

    def create_widget(self, widget_type):
        widget = eval(widget_type)()
        widget.setAlignment(Qt.AlignCenter)
        return widget

    def change_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.font_label.setFont(font)

    def change_font_size(self, size):
        font = self.font_label.font()
        font.setPointSize(size)
        self.font_label.setFont(font)

    def change_font_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.font_color_label.setStyleSheet(f"background-color: {color.name()}")
            palette = self.font_label.palette()
            palette.setColor(QPalette.WindowText, color)
            self.font_label.setPalette(palette)

    def change_background_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.background_color_label.setStyleSheet(
                f"background-color: {color.name()}"
            )
            palette = self.palette()
            palette.setColor(QPalette.Window, color)
            self.setPalette(palette)

    def get_log_history_length(self):
        return self.log_history_spinbox.value()

    def get_buffering_time(self):
        return self.buffering_time_spinbox.value()
