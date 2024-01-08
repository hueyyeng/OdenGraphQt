import importlib.util

from qtpy.QtWidgets import QCheckBox


class CustomCheckBox(QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comel_checkbox_fix(12)

    def comel_checkbox_fix(self, size=12):
        # For Comel Light/Dark theme toggle library: https://github.com/hueyyeng/Comel
        _comel = importlib.util.find_spec("comel")
        if not _comel:
            return

        self.setStyleSheet(
            f"""
                QCheckBox::indicator {{
                  width: {size}px;
                  height: {size}px;
                }}
              """
        )
        self.resize(size, size)
