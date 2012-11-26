import expr as E
from rules import (RULES, prepare_rule_arguments, bind_arguments)
from graph import Graph

def make_toy_graph():
    vertices = set(['x', 'y', 'z', 'h'])
    edges = set([('h', 'x'), ('x', 'z'), ('z', 'y'), ('h', 'y')])
    return Graph(vertices, edges)

def get_rule(name):
    return [r for r in RULES if r['name'] == name][0]


def test_claim_1():
    """
    test we can apply rule 2 forwards to rewrite pr(z|do(x)) as pr(z|x)
    """
    graph = make_toy_graph()
    bindings = {
        'z' : set(['z']),
        'x' : set(['x']),
        'y' : set(['y']),
    }
    bind = bindings.get
    root_expr = E.prob([E.v('z')], [E.do(E.v('x'))])

    rule = get_rule('ignore_intervention_act_forward')

    sites = list(rule['site_gen'](root_expr))
    assert len(sites) == 1
    site, = sites

    prepped_args = prepare_rule_arguments(rule['unpack_target'], site)
    bound_args = bind_arguments(bind, prepped_args)
    assert rule['assumption_test'](g = graph, **bound_args)

    root_expr_prime = rule['apply'](site)
    assert root_expr_prime == E.prob([E.v('z')], [E.v('x')])

def test_claim_2():
    """
    test we can apply rule 2 in reverse to rewrite pr(y|z,do(x)) as pr(y|do(z),do(x))
    """
    graph = make_toy_graph()
    bindings = {
        'z' : set(['z']),
        'x' : set(['x']),
        'y' : set(['y']),
    }
    bind = bindings.get
    root_expr = E.prob([E.v('y')], [E.v('z'), E.do(E.v('x'))])

    rule = get_rule('ignore_intervention_act_reverse')

    sites = list(rule['site_gen'](root_expr))
    assert len(sites) == 1
    site, = sites

    prepped_args = prepare_rule_arguments(rule['unpack_target'], site)
    bound_args = bind_arguments(bind, prepped_args)
    assert rule['assumption_test'](g = graph, **bound_args)

    root_expr_prime = rule['apply'](site)
    assert root_expr_prime == E.prob([E.v('y')], [E.do(E.v('z')), E.do(E.v('x'))])

def test_claim_3():
    """
    test we can apply rule 3 forwards to rewrite pr(y|do(z),do(x)) as pr(y|do(z))
    """
    graph = make_toy_graph()
    bindings = {
        'z' : set(['z']),
        'x' : set(['x']),
        'y' : set(['y']),
    }
    bind = bindings.get
    root_expr = E.prob([E.v('y')], [E.do(E.v('z')), E.do(E.v('x'))])

    rule = get_rule('ignore_intervention_entirely_forward')

    sites = list(rule['site_gen'](root_expr))
    assert len(sites) == 2
    site = sites[1]

    prepped_args = prepare_rule_arguments(rule['unpack_target'], site)
    bound_args = bind_arguments(bind, prepped_args)
    assert rule['assumption_test'](g = graph, **bound_args)

    root_expr_prime = rule['apply'](site)
    assert root_expr_prime == E.prob([E.v('y')], [E.do(E.v('z'))])

def test_claim_4():
    """
    test we can apply rule 2 forwards to rewrite pr(y|x,do(z)) as pr(y|x,z)
    """
    graph = make_toy_graph()
    bindings = {
        'z' : set(['z']),
        'x' : set(['x']),
        'y' : set(['y']),
    }
    bind = bindings.get
    root_expr = E.prob([E.v('y')], [E.v('x'), E.do(E.v('z'))])

    rule = get_rule('ignore_intervention_act_forward')

    sites = list(rule['site_gen'](root_expr))
    assert len(sites) == 1
    site, = sites

    prepped_args = prepare_rule_arguments(rule['unpack_target'], site)
    bound_args = bind_arguments(bind, prepped_args)
    assert rule['assumption_test'](g = graph, **bound_args)

    root_expr_prime = rule['apply'](site)
    assert root_expr_prime == E.prob([E.v('y')], [E.v('x'), E.v('z')])

def test_claim_5():
    """
    test we can apply rule 3 forwards to rewrite pr(x|do(z)) as pr(x)
    """
    graph = make_toy_graph()
    bindings = {
        'z' : set(['z']),
        'x' : set(['x']),
        'y' : set(['y']),
    }
    bind = bindings.get
    root_expr = E.prob([E.v('x')], [E.do(E.v('z'))])

    rule = get_rule('ignore_intervention_entirely_forward')

    sites = list(rule['site_gen'](root_expr))
    assert len(sites) == 1
    site, = sites

    prepped_args = prepare_rule_arguments(rule['unpack_target'], site)
    bound_args = bind_arguments(bind, prepped_args)
    assert rule['assumption_test'](g = graph, **bound_args)

    root_expr_prime = rule['apply'](site)
    assert root_expr_prime == E.prob([E.v('x')], [])

