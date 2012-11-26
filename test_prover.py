import expr as E
from test_rules import make_toy_graph
from proof_state import ProofState
from prover import (make_heuristic, proof_search)

def test_full_problem():
    graph = make_toy_graph()

    banned_values = set([frozenset(['h'])])
    heuristic = make_heuristic(banned_values, greed=10)

    initial_bindings = {
        'x' : set(['x']),
        'y' : set(['y']),
    }

    initial_expr = E.prob([E.v('y')], [E.do(E.v('x'))])

    initial_proof_state = ProofState(
        length = 0, # length of proof
        heuristic_length = 0,
        bindings = initial_bindings,
        root_expr = initial_expr,
    ).normalise()

    initial_proof_state = initial_proof_state.copy(heuristic_length=heuristic(initial_proof_state))

    def goal_check(proof_state):
        return proof_state.heuristic_length == 0

    result = proof_search(initial_proof_state, graph, goal_check, heuristic, max_proof_length=7)
    assert result['reached_goal']
    # print 'success!'
    # print result['path']

