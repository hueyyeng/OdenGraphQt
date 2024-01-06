from typing import TypedDict

from qtpy import QtWidgets, QtCore, QtGui

from .prop_widgets_abstract import BaseProperty


class TValidator(TypedDict):
    pattern: str
    placeholder: str
    tooltip: str
    is_case_sensitive: bool
    checkbox_visible: bool
    tool_btn_visible: bool


# Refer to NodeLineEditValidatorCheckBox
class PropLineEditValidatorCheckBox(BaseProperty):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._validator_pattern = ""
        self._validator_placeholder = ""
        self._validator_tooltip = ""
        self._validator_is_case_sensitive = False

        self._lineedit = QtWidgets.QLineEdit()
        self._lineedit.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self._lineedit.editingFinished.connect(self._on_value_change)
        self._lineedit.clearFocus()

        self._checkbox = QtWidgets.QCheckBox()
        self._checkbox.toggled.connect(self._on_value_change)
        self._checkbox_label = ""

        self._tool_btn = QtWidgets.QToolButton()
        self._tool_btn.setVisible(False)

        self._checkbox_visible = True
        self._tool_btn_visible = False

        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self._lineedit)
        hbox.addWidget(self._checkbox)
        hbox.addWidget(self._tool_btn)

    def set_validator(self, validator_data: TValidator):
        self._validator_pattern = validator_data.get("pattern")
        validator = QtGui.QRegularExpressionValidator()
        if validator_data.get("is_case_sensitive"):
            self._validator_is_case_sensitive = True
            regex = QtCore.QRegularExpression(
                self._validator_pattern,
                QtCore.QRegularExpression.PatternOption.CaseInsensitiveOption,
            )
        else:
            regex = QtCore.QRegularExpression(self._validator_pattern)

        validator.setRegularExpression(regex)
        self._lineedit.setValidator(validator)

        tooltip = validator_data.get("tooltip")
        if tooltip:
            self._validator_tooltip = tooltip
            self._lineedit.setToolTip(tooltip)

        placeholder = validator_data.get("placeholder")
        if placeholder:
            self._validator_placeholder = placeholder
            self._lineedit.setPlaceholderText(placeholder)

        self._checkbox_visible = validator_data.get("checkbox_visible", True)
        self._tool_btn_visible = validator_data.get("tool_btn_visible", True)

        self._checkbox.setVisible(self._checkbox_visible)
        self._tool_btn.setVisible(self._tool_btn_visible)

    def set_checkbox_label(self, label: str):
        self._checkbox.setText(label)

    def set_tool_btn(self, func, icon: QtGui.QIcon = None, tooltip: str = None):
        self._tool_btn.setVisible(True)
        self._tool_btn.clicked.connect(func)

        if icon is None:
            icon = QtGui.QIcon(
                self.style().standardPixmap(
                    QtWidgets.QStyle.StandardPixmap.SP_TitleBarMaxButton
                )
            )

        self._tool_btn.setIcon(icon)
        if tooltip:
            self._tool_btn.setToolTip(tooltip)

    def _on_value_change(self, value=None):
        if value is None:
            value = self.get_value()

        self.value_changed.emit(self.toolTip(), value)

    def get_value(self):
        return (
            self._lineedit.text(),
            self._checkbox.isChecked(),
            self._validator_pattern,
            self._validator_placeholder,
            self._validator_tooltip,
            self._validator_is_case_sensitive,
            self._checkbox_label,
            self._checkbox_visible,
            self._tool_btn_visible,
        )

    def set_value(self, value):
        if isinstance(value, bool):
            self._checkbox.setChecked(value)
        elif isinstance(value, str):
            self._lineedit.setText(value)
        else:
            (
                text,
                checked,
                pattern,
                placeholder,
                tooltip,
                is_case_sensitive,
                checkbox_label,
                checkbox_visible,
                tool_btn_visible,
            ) = value

            self._lineedit.setText(text)
            self._checkbox.setChecked(checked)
            self._checkbox_visible = checkbox_visible
            self._tool_btn_visible = tool_btn_visible

            if checkbox_label:
                self._checkbox_label = checkbox_label
                self.set_checkbox_label(checkbox_label)

            if pattern:
                self._validator_pattern = pattern

            if placeholder:
                self._validator_placeholder = placeholder

            if tooltip:
                self._validator_tooltip = tooltip

            if is_case_sensitive:
                self._validator_is_case_sensitive = is_case_sensitive

            data = {
                "pattern": self._validator_pattern,
                "placeholder": self._validator_placeholder,
                "tooltip": self._validator_tooltip,
                "is_case_insensitive": self._validator_is_case_sensitive,
                "checkbox_visible": self._checkbox_visible,
                "tool_btn_visible": self._tool_btn_visible,
            }
            self.set_validator(data)

        self._on_value_change(value)
