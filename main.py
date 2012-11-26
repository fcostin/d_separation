import expr as E
from test_rules import make_toy_graph
from proof_state import (ProofState, relabel_expr)
from prover import (make_heuristic, proof_search, pleasantly_fmt)

def main():
    graph = make_toy_graph()

    banned_values = set([frozenset(['h'])])
    heuristic = make_heuristic(banned_values)

    initial_bindings = {
        'x' : frozenset(['x']),
        'y' : frozenset(['y']),
    }

    initial_expr = E.prob([E.v('y')], [E.do(E.v('x'))])

    goal_expr = E.prob([], []) # XXX TODO

    initial_proof_state = ProofState(
        length = 0, # length of proof
        heuristic_length = 0,
        bindings = initial_bindings,
        root_expr = initial_expr,
        parent = None,
        comment = 'initial state',
    ).normalise()

    # this is a little silly
    initial_proof_state = initial_proof_state.copy(heuristic_length=heuristic(initial_proof_state))
    
    def goal_check(proof_state):
        return proof_state.heuristic_length == 0

    result = proof_search(initial_proof_state, graph, goal_check, heuristic, max_proof_length=7)
    assert result['reached_goal']
    print 'success!'

    display_proof(result['path'])

def display_proof(proof_state):
    proof = extract_proof(proof_state)
    for i, proof_state in enumerate(proof):
        print 'step %d' % i
        print '\tcomment:'
        print '\t\t%s'% str(proof_state.comment)
        # print '\traw_bindings:'
        # print '\t\t%s' % str(proof_state.bindings)
        # print '\traw_expr:'
        # print '\t\t%s' % str(E.fmt(proof_state.root_expr))
        print '\texpr:'
        print '\t\t%s' % pleasantly_fmt(proof_state.bindings, proof_state.root_expr)

def extract_proof(proof_state):
    proof = []
    while proof_state is not None:
        proof.append(proof_state)
        proof_state = proof_state.parent
    return list(reversed(proof))

if __name__ == '__main__':
    main()


