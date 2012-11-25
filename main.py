from graph import Graph
from partition import gen_partitions
from d_connection import is_d_connected
from ancestors import find_ancestors

def make_toy_graph():
    vertices = set(['x', 'y', 'z', 'h'])
    edges = set([('h', 'x'), ('x', 'z'), ('z', 'y'), ('h', 'y')])
    return Graph(vertices, edges)

def ignore_observations_assumption(x, y, z, w, g):
    g_xbar = g.prune_edges_to(x)
    arcs_from = g_xbar.make_arcs_from()
    return (y and z and not is_d_connected(y, z, set(w) | set(x), arcs_from))

def ignore_intervention_act_assumption(x, y, z, w, g):
    g_xbar = g.prune_edges_to(x)
    g_xbar_zunderbar = g_xbar.prune_edges_from(z)
    arcs_from = g_xbar_zunderbar.make_arcs_from()
    return (y and z and not is_d_connected(y, z, set(w) | set(x), arcs_from))

def ignore_intervention_entirely_assumption(x, y, z, w, g):
    g_xbar = g.prune_edges_to(x)
    w_ancestors = find_ancestors(set(w), g.make_arcs_from())
    zw = set(vertex for vertex in z if vertex not in w_ancestors)
    g_xbar_zwbar = g_xbar.prune_edges_to(zw)
    arcs_from = g_xbar_zwbar.make_arcs_from()
    return (y and z and not is_d_connected(y, z, set(w) | set(x), arcs_from))


def main():

    graph = make_toy_graph()

    vertices = list(sorted(list(graph.vertices)))

    partitions = list(set(tuple(map(tuple, p[:-1])) for p in gen_partitions(vertices, 5)))
    n_partitions = len(partitions)

    rules = [
        ('ignore_observations', ignore_observations_assumption),
        ('ignore_intervention_act', ignore_intervention_act_assumption),
        ('ignore_intervention_entirely', ignore_intervention_entirely_assumption),
    ]

    for i, partition in enumerate(partitions):
        x, y, z, w = partition

        can_apply = []
        for rule_name, rule_assumption in rules:
            if rule_assumption(x, y, z, w, graph):
                can_apply.append(rule_name)

        def show_subset(name, x):
            if x:
                print '\t\t%s = {%s}' % (name, ','.join(x))

        if can_apply:
            print 'partition [%d/%d]' % (i, n_partitions)
            print '\tcan apply:'
            for rule_name in can_apply:
                print '\t\t%s' % rule_name
            print '\twith'
            show_subset('X', x)
            show_subset('Y', y)
            show_subset('Z', z)
            show_subset('W', w)

if __name__ == '__main__':
    main()
