import expr as E
from rules import (RULES, prepare_rule_arguments, bind_arguments)
from proof_state import (ProofState, get_variable_order, relabel_expr)
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
            succ_heuristic = 0
            succ_bindings = dict(proof_state.bindings)
            succ_bindings[i] = value
            succ_root_expr = inject(expr_prime)

            succ_comment = 'conditioned %s on %s' % (
                pleasantly_fmt(proof_state.bindings, prob_expr),
                make_canonical_variable_name(value))

            succ_proof_state = ProofState(succ_length, succ_heuristic, succ_bindings, succ_root_expr,
                parent=proof_state, comment=succ_comment)
            yield succ_proof_state
    
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
            succ_heuristic = 0
            succ_bindings = dict(proof_state.bindings)
            succ_root_expr = rule['apply'](site)

            original_expr = site[-1]
            
            succ_comment = 'applied rule %s to %s' % (
                rule['name'],
                pleasantly_fmt(proof_state.bindings, original_expr))

            succ_proof_state = ProofState(succ_length, succ_heuristic, succ_bindings, succ_root_expr,
                parent=proof_state, comment=succ_comment)
            yield succ_proof_state

def make_expand(graph, max_proof_length, heuristic):
    universe = set(frozenset([v]) for v in graph.vertices)

    def base_expand(proof_state):
        if proof_state.length == max_proof_length:
            return
        for succ_proof_state in gen_causal_rule_moves(RULES, proof_state, graph):
            yield succ_proof_state

        for succ_proof_state in gen_condition_moves(universe, proof_state):
            yield succ_proof_state

    def expand(proof_state):
        for succ_proof_state in base_expand(proof_state):
            succ_proof_state = succ_proof_state.normalise()
            yield succ_proof_state.copy(heuristic_length=heuristic(succ_proof_state))
    return expand


def make_counter(cell):
    def counter(_):
        cell[0] += 1
    return counter

def count_dos(expr):
    count = [0]
    f = make_counter(count)
    E.filter_walk(E.is_do, f, expr)
    return count[0]

def make_banned_value_counter(banned_values, bindings):
    p = lambda expr : E.is_v(expr) and (bindings[E.unpack_v(expr)] in banned_values)
    def banned_value_counter(exprs):
        count = [0]
        f = make_counter(count)
        for expr in exprs:
            E.filter_walk(p, f, expr)
        return count[0]
    return banned_value_counter

def count_banned_value_observations(banned_values, root_expr, bindings):
    f = make_banned_value_counter(banned_values, bindings)
    count = [0]
    def g(prob_expr):
        count[0] += f(prob_expr[2])
    E.filter_walk(E.is_prob, g, root_expr)
    return count[0]

def make_heuristic(banned_values, greed=1.0):
    """
    banned_values : collection of banned values
    greed : greed parameter. values > 1.0 are inadmissable
        will not necessarily result in the shortest proof but may be effective
        at reducing the time until *some* proof is discovered
    """

    assert greed > 0.0

    def heuristic(proof_state):
        alpha = count_dos(proof_state.root_expr)
        beta = count_banned_value_observations(banned_values,
            proof_state.root_expr, proof_state.bindings)
        # trick : divide by 2 to give lower bound on
        # number of moves to goal cause we can reduce both
        # alpha and beta by 1 if we remove a do(var(banned_value))
        return 0.5 * greed * (alpha + beta)
    return heuristic

def proof_search(initial_proof_state, graph, goal_check, heuristic, max_proof_length):
    initial_paths = [initial_proof_state]
    expand = make_expand(graph, max_proof_length, heuristic)
    extract_state = lambda proof_state : proof_state.extract_state()
    result = search(initial_paths, expand, goal_check, extract_state, verbose=True)
    return result

# some stuff to help out with pretty-printing

def make_canonical_variable_name(vertex_set):
    assert len(vertex_set) == 1
    return list(vertex_set)[0]

def make_pleasant_variable_names(bindings):
    new_labels = set()
    relabel = {}
    for (k, v) in bindings.iteritems():
        new_k = make_canonical_variable_name(v)
        while new_k in new_labels:
            new_k = new_k + "'" # prime that name!
        relabel[k] = new_k
        new_labels.add(new_k)
    return relabel

def pleasantly_fmt(bindings, expr):
    new_labels = make_pleasant_variable_names(bindings)
    pleasant_expr = relabel_expr(new_labels, expr)
    return str(E.fmt(pleasant_expr))

