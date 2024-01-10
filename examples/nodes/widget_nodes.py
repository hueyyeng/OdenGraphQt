from NodeGraphQt import BaseNode
from NodeGraphQt.constants import NodePropWidgetEnum
from NodeGraphQt.widgets.node_widgets import NodeLineEditValidatorCheckBox


class DropdownMenuNode(BaseNode):
    """
    An example node with a embedded added QCombobox menu.
    """

    # unique node identifier.
    __identifier__ = 'nodes.widget'

    # initial default node name.
    NODE_NAME = 'menu'

    def __init__(self):
        super(DropdownMenuNode, self).__init__()

        # create input & output ports
        self.add_input('in 1')
        self.add_output('out 1')
        self.add_output('out 2')

        # create the QComboBox menu.
        items = ['item 1', 'item 2', 'item 3']
        self.add_combo_menu('my_menu', 'Menu Test', items=items)


class TextInputNode(BaseNode):
    """
    An example of a node with a embedded QLineEdit.
    """

    # unique node identifier.
    __identifier__ = 'nodes.widget'

    # initial default node name.
    NODE_NAME = 'text'

    def __init__(self):
        super().__init__()
        pattern = r"^[A-Za-z0-9]*$"
        placeholder = ""
        tooltip = "Valid characters: A-Z a-z 0-9"
        is_case_sensitive = True
        checkbox_label = "Use Parser?"

        # create input & output ports
        self.add_input('in')
        self.add_output('out')

        # create QLineEdit text input widget.
        self.add_text_input('my_input', 'Text Input', tab='widgets')

        tool_btn_kwargs = {
            "func": self._callback,
            "tooltip": "Awesome"
        }
        kwargs = {
            "validator": {
                "pattern": pattern,
                "placeholder": placeholder,
                "tooltip": tooltip,
                "is_case_insensitive": is_case_sensitive,
                "checkbox_visible": True,
                "tool_btn_visible": True,
            },
            "checkbox_label": checkbox_label,
            "tool_btn": tool_btn_kwargs,
        }
        node_widget = NodeLineEditValidatorCheckBox(
            "src_path",
            pattern,
            placeholder,
            tooltip,
            is_case_sensitive,
            checkbox_label,
            checkbox_visible=True,
            tool_btn_visible=True,
            widget_label="src_path",
            parent=self.view,
        )
        node_widget.get_custom_widget().set_tool_btn(**tool_btn_kwargs)
        self.add_custom_widget(
            node_widget,
            NodePropWidgetEnum.LINEEDIT_VALIDATOR_CHECKBOX.value,
            "widgets",
            **kwargs,
        )

        kwargs2 = {
            "validator": {
                "pattern": pattern,
                "placeholder": placeholder,
                "tooltip": tooltip,
                "is_case_insensitive": is_case_sensitive,
                "checkbox_visible": False,
                "tool_btn_visible": False,
            },
            "checkbox_label": "Check In Luggage?",
            "tool_btn": tool_btn_kwargs,
        }
        node_widget2 = NodeLineEditValidatorCheckBox(
            "dst_path",
            pattern,
            placeholder,
            tooltip,
            is_case_sensitive,
            "Check In Luggage?",
            checkbox_visible=False,
            tool_btn_visible=False,
            widget_label="dst_path",
            parent=self.view,
        )
        node_widget2.get_custom_widget().set_tool_btn(**tool_btn_kwargs)
        node_widget2.set_checkbox_visible(False)
        node_widget2.set_tool_btn_visible(False)
        self.add_custom_widget(
            node_widget2,
            NodePropWidgetEnum.LINEEDIT_VALIDATOR_CHECKBOX.value,
            "widgets",
            **kwargs2,
        )

    def _callback(self):
        print(f"YOU HAVE CLICKED ON '{self.NODE_NAME}'")


class CheckboxNode(BaseNode):
    """
    An example of a node with 2 embedded QCheckBox widgets.
    """

    # set a unique node identifier.
    __identifier__ = 'nodes.widget'

    # set the initial default node name.
    NODE_NAME = 'checkbox'

    def __init__(self):
        super(CheckboxNode, self).__init__()

        # create the checkboxes.
        self.add_checkbox('cb_1', '', 'Checkbox 1', True)
        self.add_checkbox('cb_2', '', 'Checkbox 2', False)

        # create input and output port.
        self.add_input('in', color=(200, 100, 0))
        self.add_output('out', color=(0, 100, 200))
