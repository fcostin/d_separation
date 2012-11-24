"""
find set of ancestors of z

where z is set of vertices from a directed graph
"""

from search import search

class SearchPath:
    def __init__(self, length, vertex):
        self.length = length
        self.vertex = vertex
        self._tuple = self.as_tuple()

    def extract_state(self):
        return self.vertex

    def as_tuple(self):
        return (self.length, self.vertex)

    def __lt__(self, other):
        return self._tuple < other._tuple

    def __gt__(self, other):
        return self._tuple > other._tuple

def follow_arc(path, arc_sign, vertex):
    return SearchPath(
        length = path.length + 1,
        vertex = vertex,
    )

def make_expand(arcs_from, feasible_sign):
    def expand(path):
        for (arc_sign, vertex) in arcs_from(path.vertex):
            if not feasible_sign(arc_sign):
                continue
            yield follow_arc(path, arc_sign, vertex)
    return expand

def has_reached_goal(path):
    return False

def find_ancestors(z, arcs_from):
    initial_paths = [SearchPath(0, vertex) for vertex in z]
    expand = make_expand(arcs_from, feasible_sign=-1)
    extract_state = lambda path : path.extract_state()
    result = search(initial_paths, expand, has_reached_goal, extract_state)
    closed = result['closed']
    z_ancestors = set(closed.keys())
    return z_ancestors

