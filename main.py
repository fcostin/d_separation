import expr as E
from test_rules import make_toy_graph
from proof_state import ProofState
from prover import (make_heuristic, proof_search, pleasantly_fmt)
import sys

def main():

    if len(sys.argv) != 2:
        sys.stderr.write('usage: greediness (positive float...)\n')
        sys.exit(1)

    greed = float(sys.argv[1])

    graph = make_toy_graph()

    banned_values = set([frozenset(['h'])])
    # dial the greed parameter up high.
    # this makes the search very optimistic.
    # in general this may not find the shortest proof
    heuristic = make_heuristic(banned_values, greed)

    initial_bindings = {
        'x' : frozenset(['x']),
        'y' : frozenset(['y']),
    }

    initial_expr = E.prob([E.v('y')], [E.do(E.v('x'))])

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

    display_proof_as_listing(result['path'])

    out_file_name = 'proof_tree.dot'
    write_proof_tree(result['path'], result['closed'], out_file_name)

def write_proof_tree(path, closed, out_file_name):

    proof = extract_proof(path)
    solution_states = set(proof_state.extract_state() for proof_state in proof)

    def make_fancy_label(proof_state):
        s = pleasantly_fmt(proof_state.bindings, proof_state.root_expr)
        rewrites = {
            'sigma' : '&#8721;',
            'product' : '&#8719;',
            "'" : '&#8242;',
        }
        for src, dst in rewrites.iteritems():
            s = s.replace(src, dst)
        return s

    with open(out_file_name, 'w') as f_out:
        def put(s):
            f_out.write(s + '\n')
        def emit_node(i, proof_state):
            label = make_fancy_label(proof_state)
            style = {
                'shape' : 'box',
                'style' : 'rounded,filled',
                'label' : label,
            }
            if proof_state.extract_state() in solution_states:
                style['fillcolor'] = 'yellow'
            else:
                style['fillcolor'] = 'grey'
            style_string = ','.join('%s="%s"' % (k, v) for (k, v) in style.iteritems())
            put('\t%s [%s];' % (i, style_string))
        def emit_arc(i, j):
            put('\t%s -> %s;' % (i, j))
        put('digraph proof_tree {')
        extract_proof_tree(closed, emit_node, emit_arc)
        put('}')

def extract_proof_tree(closed, emit_node, emit_arc):
    states = set()
    for state in closed:
        states.add(state)
    states = list(sorted(states))

    state_indices = {state:i for i, state in enumerate(states)}

    for state in states:
        i = state_indices[state]
        proof_state = closed[state]
        emit_node(i, proof_state)
        if proof_state.parent is not None:
            j = state_indices[proof_state.parent.extract_state()]
            emit_arc(j, i)


def display_proof_as_listing(proof_state):
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


