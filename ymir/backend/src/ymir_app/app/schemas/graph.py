from enum import IntEnum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .common import Common


class NodeType(IntEnum):
    dataset = 1
    model = 2


class Node(BaseModel):
    id: int
    name: str
    hash: str
    type: int
    proprieties: Optional[Dict] = None


class Task(BaseModel):
    id: int
    name: Optional[str]
    hash: Optional[str]
    type: Optional[int]
    proprieties: Optional[Dict] = None


class Edge(BaseModel):
    source: str = Field(description="node hash")
    target: str = Field(description="node hash")
    task: Task


class Graph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


class GraphOut(Common):
    result: Graph
