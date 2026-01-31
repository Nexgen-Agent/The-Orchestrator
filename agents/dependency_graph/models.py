from pydantic import BaseModel, Field
from typing import List, Dict, Any

class GraphStats(BaseModel):
    num_nodes: int
    num_edges: int
    density: float
    is_dag: bool
    circular_dependencies: List[List[str]]

class ModuleRanking(BaseModel):
    module: str
    score: float

class DependencyGraphOutput(BaseModel):
    stats: GraphStats
    shared_modules: List[str]
    leaf_modules: List[str]
    core_modules: List[str]
    adjacency_list: Dict[str, List[str]]
    centrality_ranking: List[ModuleRanking]
    graph_json: Dict[str, Any]
