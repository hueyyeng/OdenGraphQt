import signal

from qtpy import QtWidgets

from NodeGraphQt import BaseNode, NodeGraph
from NodeGraphQt.constants import PortTypeEnum
from NodeGraphQt.qgraphics.node_base import NodeItem


class PublishWriteNodeItem(NodeItem):
    def _align_widgets_horizontal(self, v_offset: int):
        if not self._widgets:
            return

        rect = self.boundingRect()
        y = rect.y() + v_offset
        for widget in self._widgets.values():
            if not widget.isVisible():
                continue

            widget_rect = widget.boundingRect()
            x = rect.center().x() - (widget_rect.width() / 2)
            widget.widget().setTitleAlign('center')
            widget.setPos(x, y)
            y += widget_rect.height()


class PrevNextNode(BaseNode):
    NODE_NAME = "Action Node"

    def __init__(self):
        super().__init__()

        # create an input port.
        self.add_input("_prev", color=(180, 80, 0), multi_input=False)

        # create an output port.
        self.add_output("_next", multi_output=False)


class FoobarNode(PrevNextNode):
    NODE_NAME = "Foobar"

    def __init__(self):
        super().__init__()
        self.add_output(
            "spam",
            color=(50, 150, 222),
        )


class SpamNode(BaseNode):
    NODE_NAME = "Spam"

    def __init__(self):
        super().__init__()
        self.add_input("spam", color=(222, 15, 0), multi_input=False)


class BasePublishNode(PrevNextNode):
    __identifier__ = "publish"
    allow_multiple_write = False

    def __init__(self):
        super().__init__()
        port = self.add_output(
            "write",
            color=(184, 150, 0),
            multi_output=self.allow_multiple_write,
        )
        port.port_item.set_accept_constraint(
            port_name="src",
            port_type=PortTypeEnum.IN.value,
            node_identifier="publish",
        )


class PublishFileActionNode(BasePublishNode):
    NODE_NAME = "Publish File"
    allow_multiple_write = False


class PublishFileToManyActionNode(BasePublishNode):
    NODE_NAME = "Publish File to Many"
    allow_multiple_write = True


class PublishWriteNode(BaseNode):
    __identifier__ = "publish"
    NODE_NAME = "Publish Write"

    def __init__(self):
        super().__init__(qgraphics_item=PublishWriteNodeItem)
        self.set_color(164, 130, 0)
        self.add_text_input("write", "Path:")

        port = self.add_input("src", multi_input=False)
        port.port_item.set_accept_constraint(
            port_name="write",
            port_type=PortTypeEnum.OUT.value,
            node_identifier="publish",
        )


if __name__ == '__main__':

    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication([])

    # create graph controller.
    graph = NodeGraph()

    # set up context menu for the node graph.
    graph.set_context_menu_from_file('../examples/hotkeys/hotkeys.json')

    # registered example nodes.
    graph.register_nodes([
        FoobarNode,
        SpamNode,
        PublishFileActionNode,
        PublishFileToManyActionNode,
        PublishWriteNode,
    ])

    # add nodes
    graph.add_node(FoobarNode())
    graph.add_node(SpamNode())
    graph.add_node(PublishFileToManyActionNode())
    graph.add_node(PublishFileActionNode())
    graph.add_node(PublishWriteNode())
    graph.auto_layout_nodes()

    # show the node graph widget.
    graph_widget = graph.widget
    graph_widget.resize(1100, 800)
    graph_widget.show()

    app.exec_()
