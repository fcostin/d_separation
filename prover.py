import expr as E
from rules import (RULES, prepare_rule_arguments, bind_arguments)
from test_rules import make_toy_graph
from proof_state import (ProofState, get_variable_order)
from search import search

def new_variable_name(bindings):
    """
    return a new variable name
    """
    for i in xrange(len(bindings) + 1):
        if i not in bindings:
            return i
    raise ValueError(bindings)

def count_sigmas(expr):
    return len(list(E.gen_matches(E.is_sigma, expr)))

def gen_condition_moves(universe, proof_state):
    """
    yield results of all possible single-vertex conditionings
    """
    def gen_expansions(value, proof_state):
        for (prob_expr, inject) in E.gen_matches(E.is_prob, proof_state.root_expr):
            prob_vars = get_variable_order(prob_expr)
            prob_values = [proof_state.bindings[v] for v in prob_vars]
            if value in prob_values:
                continue
            # prob([x],[w]) -> sigma(y, product([prob([x], [y, w]), p([y], [w])]))
            i = new_variable_name(proof_state.bindings)
            v_i = E.v(i)
            alpha_left = tuple(prob_expr[1])
            alpha_right = (v_i, ) + tuple(prob_expr[2])
            alpha = E.prob(alpha_left, alpha_right)
            beta_left = (v_i, )
            beta_right = tuple(prob_expr[2])
            beta = E.prob(beta_left, beta_right)
            expr_prime = E.sigma(v_i, E.product([alpha, beta]))

            succ_length = proof_state.length + 1
            succ_bindings = dict(proof_state.bindings)
            succ_bindings[i] = value
            succ_root_expr = inject(expr_prime)
            yield ProofState(succ_length, succ_bindings, succ_root_expr).normalise()
    
    for value in universe:
        for succ_proof_state in gen_expansions(value, proof_state):
            yield succ_proof_state


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
            yield ProofState(succ_length, succ_bindings, succ_root_expr).normalise()

def make_expand(graph, max_proof_length):
    universe = set(frozenset([v]) for v in graph.vertices)
    def expand(proof_state):
        if proof_state.length == max_proof_length:
            return
        for succ_proof_state in gen_causal_rule_moves(RULES, proof_state, graph):
            yield succ_proof_state

        if count_sigmas(proof_state.root_expr) > 2:
            return # XXX HACK to try and prune things while debugging
        for succ_proof_state in gen_condition_moves(universe, proof_state):
            yield succ_proof_state
    return expand


def has_no_dos(expr):
    for _ in E.gen_matches(E.is_do, expr):
        return False
    return True

def observes_no_banned_values(banned_values, expr, bindings):
    for prob_expr, _ in E.gen_matches(E.is_prob, expr):
        right = prob_expr[2]
        for observed_expr in right:
            for v, _ in E.gen_matches(E.is_v, observed_expr):
                name = E.unpack_v(v)
                value = bindings[name]
                if value in banned_values:
                    return False
    return True

def make_goal_check(banned_values):
    def has_reached_goal(proof_state):
        return (has_no_dos(proof_state.root_expr) and
            observes_no_banned_values(banned_values, proof_state.root_expr, proof_state.bindings))
    return has_reached_goal

def proof_search(initial_proof_state, graph, goal_check, max_proof_length):
    initial_paths = [initial_proof_state]
    expand = make_expand(graph, max_proof_length)
    extract_state = lambda proof_state : proof_state.extract_state()
    result = search(initial_paths, expand, goal_check, extract_state, verbose=True)
    return result


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
    print 'success!'
    print result['path']


if __name__ == '__main__':
    import cProfile
    import pstats

    p = cProfile.Profile()
    p.runcall(test_full_problem)
    s = pstats.Stats(p)
    s.sort_stats('cumulative').print_stats(20)
