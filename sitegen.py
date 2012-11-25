"""
take an expression tree and find all the target sites where
it may be possible to apply our causal calculus rewrite rules.

(note that we have to do do some diagram chasing on the
structural graph to decide if the assumptions of each
rewrite rule are met. none of that stuff is done here.)
"""


from expr import (is_prob, is_do, is_v, prob, do, v, gen_matches, make_list_inject,
    make_right_inject)
from util import (compose, without)

def is_prob_conditioned_on_do(expr):
    return is_prob(expr) and any(map(is_do, expr[2]))

def is_prob_conditioned_on_v(expr):
    return is_prob(expr) and any(map(is_v, expr[2]))

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
            inject = make_right_inject('prob', left, iota)
            vs, dos = gather_atoms(without(i, right))
            yield [atom], inject, left, vs, dos

def make_prob_append_inject(left, right):
    def inject(x=None, drop=False):
        if drop:
            start = ()
        else:
            start = (x, )
        return prob(left, start + tuple(right))
    return inject

def gen_birth_sites(expr):
    left, right = expr[1], expr[2]
    inject = make_prob_append_inject(left, right)
    vs, dos = gather_atoms(right)
    yield [], inject, left, vs, dos

def make_site_generator(expr_predicate, site_predicate=None, birth_site=False):
    if birth_site:
        gen_target_sites = gen_birth_sites
    else:
        gen_target_sites = lambda expr : gen_replacement_sites(site_predicate, expr)
    def gen_moves(root_expr):
        for (expr, expr_inject) in gen_matches(expr_predicate, root_expr):
            for site in gen_target_sites(expr):
                target, site_inject, left, vs, dos = site
                inject = compose(expr_inject, site_inject)
                yield (target, inject, left, vs, dos, expr)
    return gen_moves

gen_v_sites = make_site_generator(is_prob_conditioned_on_v, is_v)
gen_do_sites = make_site_generator(is_prob_conditioned_on_do, is_do)
gen_birth_sites = make_site_generator(is_prob, birth_site=True)

