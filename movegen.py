"""
take an expression tree and find all the target sites where
it may be possible to apply our causal calculus rewrite rules.

(note that we have to do do some diagram chasing on the
structural graph to decide if the assumptions of each
rewrite rule are met. none of that stuff is done here.)
"""


from expr import (is_prob, is_do, is_v)

def is_prob_conditioned_on_do(expr):
    return is_prob(expr) and any(map(is_do, expr[2]))

def is_prob_conditioned_on_v(expr):
    return is_prob(expr) and any(map(is_v, expr[2]))

def without(i, a):
    return a[:i] + a[(i+1):]

def gather_atoms(atoms):
    vs = []
    dos = []
    for atom in atoms:
        (vs if is_v(atom) else dos).append(atom)
    return vs, dos

def gen_replacement_sites(predicate, expr):
    left, right = expr[1], expr[2]
    for i, atom in enumerate(right):
        if predicate(atom):
            iota = make_list_inject(i, right)
            inject = lambda x : prob(left, iota(x))
            vs, dos = gather_atoms(without(i, right))
            yield atom, inject, left, vs, dos

def gen_birth_sites(expr):
    left, right = expr[1], expr[2]
    inject = lambda x : prob(left, [x] + list(right))
    vs, dos = gather_atoms(right)
    yield (), inject, left, vs, dos

def make_move_generator(expr_predicate, site_predicate=None, birth_site=False):
    if birth_site:
        gen_target_sites = gen_birth_sites
    else:
        gen_target_sites = lambda expr : gen_replacement_sites(site_predicate, expr)
    def gen_moves(root_expr):
        for (expr, expr_inject) in gen_matches(expr_predicate, root_expr):
            for site in gen_target_sites(expr):
                atom, site_inject, left, vs, dos = site
                inject = lambda x : expr_inject(site_inject(x))
                yield (atom, inject, left, vs, dos)
    return gen_moves

gen_v_moves = make_move_generator(is_prob_conditioned_on_v, is_v)
gen_do_moves = make_move_generator(is_prob_conditioned_on_do, is_do)
gen_birth_moves = make_move_generator(is_prob, birth_site=True)
