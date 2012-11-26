from d_connection import is_d_connected
from ancestors import find_ancestors


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

