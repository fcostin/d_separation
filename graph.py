"""
basic graph datatype
"""

class Graph:
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges

    def flip(self):
        edges_prime = set((v, u) for (u, v) in self.edges)
        return Graph(set(self.vertices), edges_prime)

    def prune_edges_from(self, vertices):
        edges_prime = set()
        for (u, v) in self.edges:
            if u in vertices:
                continue
            edges_prime.add((u, v))
        return Graph(set(self.vertices), edges_prime)

    def prune_edges_to(self, vertices):
        return self.flip().prune_edges_from(vertices).flip()

    def make_succs(self):
        succs = {}
        for (u, v) in self.edges:
            for sign, src, dst in ((1, u, v), (-1, v, u)):
                if src not in succs:
                    succs[src] = set()
                succs[src].add((sign, dst))
        return succs

    def make_arcs_from(self):
        succs = self.make_succs()
        def arcs_from(u):
            for (sign, v) in succs.get(u, ()):
                yield (sign, v)
        return arcs_from

