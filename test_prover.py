import expr as E
from test_rules import make_toy_graph
from proof_state import ProofState
from prover import (make_goal_check, proof_search)

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

    banned_values = set([frozenset(['h'])])
    goal_check = make_goal_check(banned_values)
    result = proof_search(initial_proof_state, graph, goal_check, max_proof_length=7)
    assert result['reached_goal']
    # print 'success!'
    # print result['path']

