import json
from typing import Dict, Generator, List, Optional, Tuple, Union

from redis import StrictRedis
from redisgraph import Edge, Graph, Node, Path


class YmirNode(Node):
    @classmethod
    def from_dict(cls, node: Dict) -> Node:
        """
        required keys for node:
        - id: model_id or dataset_id
        - label: `Model` or `Dataset`
        """
        node["type"] = 1 if node["label"] == "Dataset" else 2
        return cls(node["id"], label=node["label"], properties=node)


class YmirTask(Edge):
    @classmethod
    def from_dicts(cls, source: Dict, target: Dict, task: Dict) -> Edge:
        src_node = YmirNode.from_dict(source)
        dest_node = YmirNode.from_dict(target)
        return cls(src_node, "Task", dest_node, task["id"], properties=task)


class GraphClient:
    def __init__(self, redis_uri: Optional[str]):
        self.redis_con = self._get_redis_con(redis_uri)
        self._graph = None
        self._user_id = None  # type: Optional[int]

    @property
    def user_id(self) -> Optional[int]:
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int) -> None:
        self._user_id = user_id

    @property
    def graph(self) -> Graph:
        return self._get_graph()

    def _get_redis_con(self, redis_uri: Optional[str]) -> StrictRedis:
        if redis_uri:
            redis_con = StrictRedis.from_url(redis_uri)
        else:
            redis_con = StrictRedis()
        return redis_con

    def _get_graph(self) -> Graph:
        name = f"graph{self.user_id:0>4}"
        graph = Graph(name, self.redis_con)
        return graph

    def query(self, query: str) -> Graph:
        """
        Query against user's graph,
        typically return history of specific node
        """
        return self.graph.query(query)

    def add_node(self, node: Union[YmirNode, Dict]) -> Graph:
        """
        Append a single node to user's graph:
        node should be Dataset or Model
        """
        if isinstance(node, dict):
            node = YmirNode.from_dict(node)
        self.graph.add_node(node)
        self.graph.commit()
        return node

    def add_relationship(self, source: Dict, target: Dict, task: Dict) -> Graph:
        """
        Append a new node to user's graph with relationship:
        node should be Dataset or Model,
        relationship is corresponding Task
        """
        relationship = YmirTask.from_dicts(source, target, task)

        s = relationship.src_node
        t = relationship.dest_node
        query = f"""\
MERGE (source:{s.label} {s.toString()})
MERGE (target:{t.label} {t.toString()})
MERGE (source) -[task:TASK {relationship.toString()}]-> (target)
RETURN source, task, target"""
        return self.query(query)

    def query_history(self, source: Dict, max_hops: int) -> Dict:
        """
        Get all the related node pointing to source node within max_hops

        source: label, id, hash
        """
        nodes = []
        edges = []
        for nodes_, edges_ in self.query_path(source["hash"], max_hops):
            nodes += nodes_
            edges += edges_

        nodes = remove_duplicated_dict(nodes)
        edges = remove_duplicated_dict(edges)
        return {
            "nodes": nodes,
            "edges": edges,
        }

    def query_path(self, hash: str, max_hops: int) -> Generator:
        # todo
        #  Cannot explicitly use `:Task` label, don't know why
        q = f"""\
MATCH p = (s) <-[task*1..{max_hops}]- (e)
WHERE s.hash = "{hash}"
RETURN p"""
        res = self.query(q)
        for record in res.result_set:
            for path in record:
                yield self.parse_path(path)

    def parse_path(self, path: Path) -> Tuple[List, List]:
        nodes = {n.id: n.properties for n in path.nodes()}
        edges = [
            {
                "source": nodes[e.src_node]["hash"],
                "target": nodes[e.dest_node]["hash"],
                "task": e.properties,
            }
            for e in path.edges()
        ]
        return list(nodes.values()), edges

    def close(self) -> None:
        print("bye")


def remove_duplicated_dict(li: List[Dict]) -> List:
    tmp = {json.dumps(i, sort_keys=True) for i in li}
    return [json.loads(i) for i in tmp]
