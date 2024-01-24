from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from OdenGraphQt import NodeObject
    from OdenGraphQt.qgraphics.port import PortItem

from OdenGraphQt.base.commands import (
    NodeInputConnectedCmd,
    NodeInputDisconnectedCmd,
    PortConnectedCmd,
    PortDisconnectedCmd,
    PortLockedCmd,
    PortUnlockedCmd,
    PortVisibleCmd,
)
from OdenGraphQt.base.model import PortModel
from OdenGraphQt.constants import PortTypeEnum
from OdenGraphQt.errors import PortError


class Port(object):
    """
    The ``Port`` class is used for connecting one node to another.

    .. inheritance-diagram:: OdenGraphQt.Port

    .. image:: _images/port.png
        :width: 50%

    See Also:
        For adding a ports into a node see:
        :meth:`BaseNode.add_input`, :meth:`BaseNode.add_output`

    Args:
        node (OdenGraphQt.NodeObject): parent node.
        port_item (PortItem): graphic item used for drawing.
    """

    def __init__(self, node, port_item):
        self.__port_item_view = port_item
        self.__model = PortModel(node)
        self.__node = node

    def __repr__(self):
        port = str(self.__class__.__name__)
        return '<{}("{}") object at {}>'.format(
            port, self.name(), hex(id(self)))

    @property
    def port_item(self) -> PortItem:
        return self.__port_item_view

    @property
    def port_node(self) -> NodeObject:
        return self.__node

    @property
    def view(self):
        """
        Returns the :class:`QtWidgets.QGraphicsItem` used in the scene.

        Returns:
            OdenGraphQt.qgraphics.port.PortItem: port item.
        """
        return self.__port_item_view

    @property
    def model(self):
        """
        Returns the port model.

        Returns:
            OdenGraphQt.base.model.PortModel: port model.
        """
        return self.__model

    def type_(self):
        """
        Returns the port type.

        Port Types:
            - :attr:`OdenGraphQt.constants.IN_PORT` for input port
            - :attr:`OdenGraphQt.constants.OUT_PORT` for output port

        Returns:
            str: port connection type.
        """
        return self.model.type_

    def multi_connection(self):
        """
        Returns if the ports is a single connection or not.

        Returns:
            bool: false if port is a single connection port
        """
        return self.model.multi_connection

    def node(self):
        """
        Return the parent node.

        Returns:
            OdenGraphQt.BaseNode: parent node object.
        """
        return self.model.node

    def name(self):
        """
        Returns the port name.

        Returns:
            str: port name.
        """
        return self.model.name

    def visible(self):
        """
        Port visible in the node graph.

        Returns:
            bool: true if visible.
        """
        return self.model.visible

    def set_visible(self, visible=True, push_undo=True):
        """
        Sets weather the port should be visible or not.

        Args:
            visible (bool): true if visible.
            push_undo (bool): register the command to the undo stack. (default: True)
        """

        # prevent signals from causing an infinite loop.
        if visible == self.visible():
            return

        undo_cmd = PortVisibleCmd(self, visible)
        if push_undo:
            undo_stack = self.node().graph.undo_stack()
            undo_stack.push(undo_cmd)
        else:
            undo_cmd.redo()

    def locked(self):
        """
        Returns the locked state.

        If ports are locked then new pipe connections can't be connected
        and current connected pipes can't be disconnected.

        Returns:
            bool: true if locked.
        """
        return self.model.locked

    def lock(self):
        """
        Lock the port so new pipe connections can't be connected and
        current connected pipes can't be disconnected.

        This is the same as calling :meth:`Port.set_locked` with the arg
        set to ``True``
        """
        self.set_locked(True, connected_ports=True)

    def unlock(self):
        """
        Unlock the port so new pipe connections can be connected and
        existing connected pipes can be disconnected.

        This is the same as calling :meth:`Port.set_locked` with the arg
        set to ``False``
        """
        self.set_locked(False, connected_ports=True)

    def set_locked(self, state=False, connected_ports=True, push_undo=True):
        """
        Sets the port locked state. When locked pipe connections can't be
        connected or disconnected from this port.

        Args:
            state (Bool): port lock state.
            connected_ports (Bool): apply to lock state to connected ports.
            push_undo (bool): register the command to the undo stack. (default: True)
        """

        # prevent signals from causing an infinite loop.
        if state == self.locked():
            return

        graph = self.node().graph
        undo_stack = graph.undo_stack()
        if state:
            undo_cmd = PortLockedCmd(self)
        else:
            undo_cmd = PortUnlockedCmd(self)
        if push_undo:
            undo_stack.push(undo_cmd)
        else:
            undo_cmd.redo()
        if connected_ports:
            for port in self.connected_ports():
                port.set_locked(state,
                                connected_ports=False,
                                push_undo=push_undo)

    def connected_ports(self):
        """
        Returns all connected ports.

        Returns:
            list[OdenGraphQt.Port]: list of connected ports.
        """
        ports = []
        graph = self.node().graph
        for node_id, port_names in self.model.connected_ports.items():
            for port_name in port_names:
                node = graph.get_node_by_id(node_id)
                if self.type_() == PortTypeEnum.IN.value:
                    ports.append(node.outputs()[port_name])
                elif self.type_() == PortTypeEnum.OUT.value:
                    ports.append(node.inputs()[port_name])
        return ports

    def connect_to(self, target_port=None, push_undo=True):
        """
        Create connection to the specified port and emits the
        :attr:`NodeGraph.port_connected` signal from the parent node graph.

        Args:
            target_port (OdenGraphQt.Port): port object.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        if not target_port:
            return

        is_valid_accept_constraint = target_port.port_item.validate_accept_constraint(self.port_item)
        if not is_valid_accept_constraint and self in target_port.connected_ports():
            return

        if self.locked() or target_port.locked():
            name = [p.name() for p in [self, target_port] if p.locked()][0]
            raise PortError(
                'Can\'t connect port because "{}" is locked.'.format(name))

        own_node_type = self.node().type_
        target_node_type = target_port.node().type_

        # validate accept connection.
        target_accepted_types = target_port.accepted_port_types().get(own_node_type)
        if target_accepted_types:
            accepted_pnames = target_accepted_types.get(self.type_()) or set([])
            if self.name() not in accepted_pnames:
                return
        own_accepted_types = self.accepted_port_types().get(target_node_type)
        if own_accepted_types:
            accepted_pnames = own_accepted_types.get(target_port.type_()) or set([])
            if target_port.name() not in accepted_pnames:
                return

        # validate reject connection.
        target_rejected_types = target_port.rejected_port_types().get(own_node_type)
        if target_rejected_types:
            rejected_pnames = target_rejected_types.get(self.type_()) or set([])
            if self.name() in rejected_pnames:
                return
        own_rejected_types = self.rejected_port_types().get(target_node_type)
        if own_rejected_types:
            rejected_pnames = own_rejected_types.get(target_port.type_()) or set([])
            if target_port.name() in rejected_pnames:
                return

        # make the connection from here.
        graph = self.node().graph
        viewer = graph.viewer()

        # FIXME: undo_stack needs to be declare early or outside or try except blah
        if push_undo:
            undo_stack = graph.undo_stack()
            undo_stack.beginMacro('connect port')

        pre_conn_port = None
        src_conn_ports = self.connected_ports()
        if not self.multi_connection() and src_conn_ports:
            pre_conn_port = src_conn_ports[0]

        if not target_port:
            if pre_conn_port:
                if push_undo:
                    undo_stack.push(PortDisconnectedCmd(self, target_port))
                    undo_stack.push(NodeInputDisconnectedCmd(self, target_port))
                    undo_stack.endMacro()
                else:
                    PortDisconnectedCmd(self, target_port).redo()
                    NodeInputDisconnectedCmd(self, target_port).redo()
            return

        if graph.acyclic() and viewer.acyclic_check(self.view, target_port.view):
            if not is_valid_accept_constraint and pre_conn_port:
                if push_undo:
                    undo_stack.push(PortDisconnectedCmd(self, pre_conn_port))
                    undo_stack.push(NodeInputDisconnectedCmd(
                        self, pre_conn_port))
                    undo_stack.endMacro()
                else:
                    PortDisconnectedCmd(self, pre_conn_port).redo()
                    NodeInputDisconnectedCmd(self, pre_conn_port).redo()
                return

        trg_conn_ports = target_port.connected_ports()
        if not target_port.multi_connection() and trg_conn_ports:
            detached_port = trg_conn_ports[0]
            if push_undo:
                undo_stack.push(PortDisconnectedCmd(target_port, detached_port))
                undo_stack.push(NodeInputDisconnectedCmd(target_port, detached_port))
            else:
                PortDisconnectedCmd(target_port, detached_port).redo()
                NodeInputDisconnectedCmd(target_port, detached_port).redo()
        if pre_conn_port:
            if push_undo:
                undo_stack.push(PortDisconnectedCmd(self, pre_conn_port))
                undo_stack.push(NodeInputDisconnectedCmd(self, pre_conn_port))
            else:
                PortDisconnectedCmd(self, pre_conn_port).redo()
                NodeInputDisconnectedCmd(self, pre_conn_port).redo()

        if push_undo:
            undo_stack.push(PortConnectedCmd(self, target_port))
            undo_stack.push(NodeInputConnectedCmd(self, target_port))
            undo_stack.endMacro()
        else:
            PortConnectedCmd(self, target_port).redo()
            NodeInputConnectedCmd(self, target_port).redo()

        # emit "port_connected" signal from the parent graph.
        ports = {p.type_(): p for p in [self, target_port]}
        graph.port_connected.emit(ports[PortTypeEnum.IN.value],
                                  ports[PortTypeEnum.OUT.value])

    def disconnect_from(self, target_port=None, push_undo=True):
        """
        Disconnect from the specified port and emits the
        :attr:`NodeGraph.port_disconnected` signal from the parent node graph.

        Args:
            target_port (OdenGraphQt.Port): port object.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        if not target_port:
            return

        if self.locked() or target_port.locked():
            name = [p.name() for p in [self, target_port] if p.locked()][0]
            raise PortError(
                'Can\'t disconnect port because "{}" is locked.'.format(name))

        graph = self.node().graph
        if push_undo:
            graph.undo_stack().beginMacro('disconnect port')
            graph.undo_stack().push(PortDisconnectedCmd(self, target_port))
            graph.undo_stack().push(NodeInputDisconnectedCmd(self, target_port))
            graph.undo_stack().endMacro()
        else:
            PortDisconnectedCmd(self, target_port).redo()
            NodeInputDisconnectedCmd(self, target_port).redo()

        # emit "port_disconnected" signal from the parent graph.
        ports = {p.type_(): p for p in [self, target_port]}
        graph.port_disconnected.emit(ports[PortTypeEnum.IN.value],
                                     ports[PortTypeEnum.OUT.value])

    def clear_connections(self, push_undo=True):
        """
        Disconnect from all port connections and emit the
        :attr:`NodeGraph.port_disconnected` signals from the node graph.

        See Also:
            :meth:`Port.disconnect_from`,
            :meth:`Port.connect_to`,
            :meth:`Port.connected_ports`

        Args:
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        if self.locked():
            err = 'Can\'t clear connections because port "{}" is locked.'
            raise PortError(err.format(self.name()))

        if not self.connected_ports():
            return

        if push_undo:
            graph = self.node().graph
            undo_stack = graph.undo_stack()
            undo_stack.beginMacro('"{}" clear connections')
            for cp in self.connected_ports():
                self.disconnect_from(cp)
            undo_stack.endMacro()
        else:
            for cp in self.connected_ports():
                self.disconnect_from(cp, push_undo=False)

    def add_accept_port_type(self, port_name, port_type, node_type):
        """
        Add a constrain to "accept" a pipe connection.

        Once a constrain has been added only ports of that type specified will
        be allowed a pipe connection.

        `Implemented in` ``v0.6.0``

        See Also:
            :meth:`OdenGraphQt.Port.add_reject_ports_type`,
            :meth:`OdenGraphQt.BaseNode.add_accept_port_type`

        Args:
            port_name (str): name of the port.
            port_type (str): port type.
            node_type (str): port node type.
        """
        # storing the connection constrain at the graph level instead of the
        # port level so we don't serialize the same data for every port
        # instance.
        self.node().add_accept_port_type(
            port=self,
            port_type_data={
                'port_name': port_name,
                'port_type': port_type,
                'node_type': node_type,
            }
        )

    def accepted_port_types(self):
        """
        Returns a dictionary of connection constrains of the port types
        that allow for a pipe connection to this node.

        See Also:
            :meth:`OdenGraphQt.BaseNode.accepted_port_types`

        Returns:
            dict: {<node_type>: {<port_type>: [<port_name>]}}
        """
        return self.node().accepted_port_types(self)

    def add_reject_port_type(self, port_name, port_type, node_type):
        """
        Add a constrain to "reject" a pipe connection.

        Once a constrain has been added only ports of that type specified will
        be rejected a pipe connection.

        `Implemented in` ``v0.6.0``

        See Also:
            :meth:`OdenGraphQt.Port.add_accept_ports_type`,
            :meth:`OdenGraphQt.BaseNode.add_reject_port_type`

        Args:
            port_name (str): name of the port.
            port_type (str): port type.
            node_type (str): port node type.
        """
        # storing the connection constrain at the graph level instead of the
        # port level, so we don't serialize the same data for every port
        # instance.
        self.node().add_reject_port_type(
            port=self,
            port_type_data={
                'port_name': port_name,
                'port_type': port_type,
                'node_type': node_type,
            }
        )

    def rejected_port_types(self):
        """
        Returns a dictionary of connection constrains of the port types
        that are NOT allowed for a pipe connection to this node.

        See Also:
            :meth:`OdenGraphQt.BaseNode.rejected_port_types`

        Returns:
            dict: {<node_type>: {<port_type>: [<port_name>]}}
        """
        return self.node().rejected_port_types(self)

    @property
    def color(self):
        return self.__port_item_view.color

    @color.setter
    def color(self, color=(0, 0, 0, 255)):
        self.__port_item_view.color = color

    @property
    def border_color(self):
        return self.__port_item_view.border_color

    @border_color.setter
    def border_color(self, color=(0, 0, 0, 255)):
        self.__port_item_view.border_color = color
