from enum import Enum
from dataclasses import dataclass

@dataclass
class AlgorithmMetadata:
    display_name: str
    complexity: str
    description: str

class AlgorithmType(Enum):
    DFS = AlgorithmMetadata(
        display_name="Depth First Search",
        complexity="O(V + E)",
        description="Explores maze by going as deep as possible before backtracking"
    )
    BFS = AlgorithmMetadata(
        display_name="Breadth First Search",
        complexity="O(V + E)",
        description="Explores maze level by level"
    )
    ASTAR = AlgorithmMetadata(
        display_name="A* Search",
        complexity="O(E log V)",
        description="Finds shortest path using heuristic search"
    )
    PRIM = AlgorithmMetadata(
        display_name="Prim's Algorithm",
        complexity="O(E log V)",
        description="Generates maze using minimum spanning tree"
    )

    @property
    def meta(self):
        return self.value
