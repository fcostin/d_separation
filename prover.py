import expr as E
from rules import (RULES, prepare_rule_arguments, bind_arguments)
from test_rules import make_toy_graph
from proof_state import ProofState
from search import search

def new_binding(bindings, value):
    """
    return a new variable (not already seen in bindings) for given value

    there is no requirement that value is distinct from any of the
    currently bound values
    """
    pass

def gen_conditionings(bindings, root_expr):
    """
    yield all possible conditionings to consider

    yields (bindings_prime, root_expr_prime)
    """
    pass



def gen_causal_rule_moves(rules, proof_state, graph):
    def bind(name):
        return proof_state.bindings[name]

    for rule in rules:
        for site in rule['site_gen'](proof_state.root_expr):
            prepped_args = prepare_rule_arguments(rule['unpack_target'], site)
            bound_args = bind_arguments(bind, prepped_args)
            if not rule['assumption_test'](g = graph, **bound_args):
                continue
            succ_length = proof_state.length + 1
            succ_bindings = dict(proof_state.bindings)
            succ_root_expr = rule['apply'](site)
            yield ProofState(succ_length, succ_bindings, succ_root_expr)

def make_expand(graph):
    # universe = set(frozenset([v]) for v in graph.vertices)
    def expand(proof_state):
        for succ_proof_state in gen_causal_rule_moves(RULES, proof_state, graph):
            yield succ_proof_state
    return expand

def make_goal_check(goal_expr, max_proof_length=10):
    # XXX this goal check is flawed in three ways:
    #
    # 1.    the goal_expr needs to be instantiated with the bound values of the variables
    #
    # 2.    we need to instantiate the proof_state.root_expr with its own bound values,
    #       since those symbols have been rewritten during normalisation
    #
    # 3.    we cant just instantiate the index of the sum! but we do need to state
    #       the domain that the sum is running over!
    #
    def has_reached_goal(proof_state):
        return (proof_state.root_expr == goal_expr) or (proof_state.length > max_proof_length)
    return has_reached_goal


def proof_search(initial_proof_state, graph, goal_expr):
    initial_paths = [initial_proof_state]
    expand = make_expand(graph)
    has_reached_goal = make_goal_check(goal_expr)
    extract_state = lambda proof_state : proof_state.extract_state()
    result = search(initial_paths, expand, has_reached_goal, extract_state)
    return result


def test_first_sub_problem():
    graph = make_toy_graph()

    initial_bindings = {
        'x' : set(['x']),
        'y' : set(['y']),
        'z' : set(['z']),
    }

    initial_expr = E.sigma(E.v('z'), E.product([
        E.prob([E.v('y')], [E.v('z'), E.do(E.v('x'))]),
        E.prob([E.v('z')], [E.do(E.v('x'))])]))

    initial_proof_state = ProofState(
        length = 0, # length of proof
        bindings = initial_bindings,
        root_expr = initial_expr,
    ).normalise()

    print initial_proof_state.bindings
    print initial_proof_state.root_expr

    goal_expr = E.sigma(E.v('z'), E.product([
        E.prob([E.v('y')], [E.v('z'), E.do(E.v('x'))]),
        E.prob([E.v('z')], [E.v('x')])]))

    result = proof_search(initial_proof_state, graph, goal_expr)
    assert result['reached_goal']



def test_full_problem():
    graph = make_toy_graph()

    initial_bindings = {
        'x' : set(['x']),
        'y' : set(['y']),
    }

    initial_expr = E.prob([E.v('y')], [E.do(E.v('x'))])

    goal_expr = E.prob([], []) # XXX TODO

    initial_proof_state = ProofState(
        length = 0, # length of proof
        bindings = initial_bindings,
        root_expr = initial_expr,
    ).normalise()

    result = proof_search(initial_proof_state, graph, goal_expr)
    assert result['reached_goal']


