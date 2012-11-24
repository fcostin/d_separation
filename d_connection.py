"""
determine if x and y are d-connected given z

where x, y, z are sets of vertices from a directed graph

x and y are d-connected given z if there exists an unblocked path
from x to y given z.

the existence of such a path may be posed as a shortest-path problem,
which we may solve via Dijkstra's algorithm.
"""

from search import search
from ancestors import find_ancestors

class SearchPath:
    def __init__(self, length, vertex, parent_vertex, parent_sign, grandparent_sign):
        self.length = length
        self.vertex = vertex
        self.parent_vertex = parent_vertex
        self.parent_sign = parent_sign
        self.grandparent_sign = grandparent_sign
        self._tuple = self.as_tuple()

    def extract_state(self):
        return (self.vertex, self.parent_vertex, self.parent_sign, self.grandparent_sign)

    def as_tuple(self):
        return (self.length, self.vertex, self.parent_vertex, self.parent_sign, self.grandparent_sign)

    def __lt__(self, other):
        return self._tuple < other._tuple

    def __gt__(self, other):
        return self._tuple > other._tuple

def follow_arc(path, arc_sign, vertex):
    return SearchPath(
        length = path.length + 1,
        vertex = vertex,
        parent_vertex = path.vertex,
        parent_sign = arc_sign,
        grandparent_sign = path.parent_sign
    )

def has_traverse(path):
    return (path.parent_sign in (-1, 1)) and (path.parent_sign == path.grandparent_sign)

def has_fork(path):
    return path.parent_sign == 1 and path.grandparent_sign == -1

def has_collider(path):
    return path.parent_sign == -1 and path.grandparent_sign == 1

def make_blocked_predicate(z, z_ancestors):
    def is_blocked(path):
        return (
            (has_collider(path) and path.vertex not in z_ancestors) or
            (has_traverse(path) and path.vertex in z) or
            (has_fork(path) and path.vertex in z)
        )
    return is_blocked

def make_expand(arcs_from, is_blocked):
    def expand(path):
        for (arc_sign, vertex) in arcs_from(path.vertex):
            succ_path = follow_arc(path, arc_sign, vertex)
            if not is_blocked(succ_path):
                yield succ_path
    return expand

def make_goal_test(y):
    def has_reached_goal(path):
        return path.vertex in y
    return has_reached_goal

def is_d_connected(x, y, z, arcs_from):
    initial_paths = [SearchPath(0, vertex, vertex, 0, 0) for vertex in x]
    z_ancestors = find_ancestors(z, arcs_from)
    is_blocked = make_blocked_predicate(z, z_ancestors)
    expand = make_expand(arcs_from, is_blocked)
    has_reached_goal = make_goal_test(y)
    extract_state = lambda path : path.extract_state()
    result = search(initial_paths, expand, has_reached_goal, extract_state)
    return result['reached_goal']

