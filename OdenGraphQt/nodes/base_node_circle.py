#!/usr/bin/python
from OdenGraphQt.nodes.base_node import BaseNode
from OdenGraphQt.qgraphics.node_circle import CircleNodeItem


class BaseNodeCircle(BaseNode):
    """
    `Implemented in` ``v0.5.2``

    The ``OdenGraphQt.BaseNodeCircle`` is pretty much the same class as the
    :class:`OdenGraphQt.BaseNode` except with a different design.

    .. inheritance-diagram:: OdenGraphQt.BaseNodeCircle

    .. image:: ../_images/node_circle.png
        :width: 250px

    example snippet:

    .. code-block:: python
        :linenos:

        from OdenGraphQt import BaseNodeCircle

        class ExampleNode(BaseNodeCircle):

            # unique node identifier domain.
            __identifier__ = 'io.jchanvfx.github'

            # initial default node name.
            NODE_NAME = 'My Node'

            def __init__(self):
                super(ExampleNode, self).__init__()

                # create an input port.
                self.add_input('in')

                # create an output port.
                self.add_output('out')
    """

    NODE_NAME = 'Circle Node'

    def __init__(self, qgraphics_item=None):
        super(BaseNodeCircle, self).__init__(qgraphics_item or CircleNodeItem)
