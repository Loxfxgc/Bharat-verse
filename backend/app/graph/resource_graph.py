"""
BharatVerse - Resource Graph Layer
Provides graph modeling for Campus Resources:
Nodes: Building, Room, Faculty, Course, Equipment
Relationships: LOCATED_IN, TAUGHT_BY, REQUIRES_CAPABILITY, SCHEDULED_IN, INSTALLED_IN
Uses NetworkX in-memory graph with seamless queries.
"""

import os
import json
import networkx as nx

GRAPH_DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "synthetic", "graph_nodes_edges.json")
)

class CampusResourceGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.load_graph()

    def load_graph(self):
        if not os.path.exists(GRAPH_DATA_PATH):
            return

        with open(GRAPH_DATA_PATH, "r") as f:
            data = json.load(f)

        self.graph.clear()
        for node in data.get("nodes", []):
            self.graph.add_node(node["id"], **node)

        for edge in data.get("edges", []):
            self.graph.add_edge(edge["source"], edge["target"], relation=edge.get("relation", "CONNECTED_TO"))

    def get_graph_data(self):
        nodes_list = []
        for n, attrs in self.graph.nodes(data=True):
            nodes_list.append({
                "id": n,
                "label": attrs.get("label", "Node"),
                "name": attrs.get("name", n),
                "capacity": attrs.get("capacity", None),
                "dept": attrs.get("dept", None)
            })

        edges_list = []
        for u, v, attrs in self.graph.edges(data=True):
            edges_list.append({
                "source": u,
                "target": v,
                "relation": attrs.get("relation", "CONNECTED_TO")
            })

        return {"nodes": nodes_list, "edges": edges_list}

    def get_course_context(self, course_id: str):
        if course_id not in self.graph:
            return None

        course_data = dict(self.graph.nodes[course_id])
        faculty = []
        room = None
        required_caps = []

        for _, target, data in self.graph.out_edges(course_id, data=True):
            rel = data.get("relation")
            if rel == "TAUGHT_BY" and target in self.graph:
                faculty.append(dict(self.graph.nodes[target]))
            elif rel == "SCHEDULED_IN" and target in self.graph:
                room = dict(self.graph.nodes[target])
            elif rel == "REQUIRES_CAPABILITY":
                required_caps.append(target)

        return {
            "course": course_data,
            "faculty": faculty[0] if faculty else None,
            "current_room": room,
            "required_capabilities": required_caps
        }

    def find_capable_rooms(self, required_capabilities: list, min_capacity: int = 0):
        capable_rooms = []
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("label") == "Room":
                cap = attrs.get("capacity", 0)
                if cap >= min_capacity:
                    capable_rooms.append(attrs)
        return capable_rooms

campus_graph = CampusResourceGraph()
