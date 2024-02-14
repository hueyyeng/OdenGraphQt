from __future__ import annotations

from typing_extensions import NotRequired, TypedDict


class TSDGraph(TypedDict):
    acyclic: bool
    pipe_style: int
    pipe_slicing: bool
    pipe_collision: bool
    layout_direction: int
    accept_connection_types: dict
    reject_connection_types: dict


T_PORTS = dict[str, dict[str, list[str]]]


class TSDNode(TypedDict):
    pos: list[int]  # Actually tuple[int, int]
    icon: str | None
    name: str
    color: list[int]  # tuple[int, int, int, int]
    type_: str
    width: float
    height: float
    custom: dict
    visible: bool
    disabled: bool
    selected: bool
    text_color: list[int]  # tuple[int, int, int, int]
    border_color: list[int]  # tuple[int, int, int, int]
    layout_direction: int
    input_ports: NotRequired[T_PORTS]
    output_ports: NotRequired[T_PORTS]
    subgraph_session: dict
    port_deletion_allowed: bool


TSDConnections = TypedDict(
    "TSDConnections",
    {
        "in": list[str],  # Technically tuple[str, str] but JSON so pain peko
        "out": list[str],  # tuple[int, int]
    }
)


class TSerializedData(TypedDict):
    graph: TSDGraph
    nodes: dict[str, TSDNode]
    connections: NotRequired[list[TSDConnections]]
