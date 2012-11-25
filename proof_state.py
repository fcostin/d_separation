from util import freeze_dict
from expr import (is_v, unpack_v, gen_matches, normalise_expr)
from expr import v as v_


class ProofState:
    def __init__(self, length, bindings, root_expr):
        self.length = length
        self.bindings = bindings
        self.root_expr = root_expr
        self._tuple = self.as_tuple()

    def normalise(self, max_iters=None):
        expr = self.root_expr
        bindings = self.bindings
        i = 0
        while max_iters is None or i < max_iters:
            i += 1
            expr_prime = normalise_expr(expr)
            v_order = get_variable_order(expr_prime)
            new_labels = make_normal_relabeling(v_order)
            bindings_prime = relabel_bindings(new_labels, bindings)
            expr_prime_prime = relabel_expr(new_labels, expr_prime)
            if expr_prime_prime == expr:
                break
            bindings = bindings_prime
            expr = expr_prime_prime

        return ProofState(self.length, bindings_prime, expr_prime_prime)

    def extract_state(self):
        # XXX todo freeze bindings
        bindings = freeze_dict(self.bindings)
        return (bindings, self.root_expr)

    def as_tuple(self):
        return (self.length, ) + self.extract_state()

    def __lt__(self, other):
        self._tuple < other._tuple

    def __gt(self, other):
        self._tuple > other._tuple

# utilities required to normalise the proof state

def get_variable_order(root_expr):
    touched = set()
    order = []
    for v, _ in gen_matches(is_v, root_expr):
        if v in touched:
            continue
        touched.add(v)
        order.append(unpack_v(v))
    return order

def make_normal_relabeling(variable_order):
    relabel = {}
    for i, v in enumerate(variable_order):
        relabel[v] = i
    return relabel

def relabel_bindings(new_labels, bindings):
    new_bindings = {}
    for k, v in bindings.iteritems():
        if k not in new_labels:
            continue
        new_bindings[new_labels[k]] = v
    return new_bindings

def replace_all_in_expr(expr, old, new):
    if old == new:
        return expr
    p = lambda e : e == old
    fixed_point = False
    while not fixed_point:
        fixed_point = True
        for v, inject in gen_matches(p, expr):
            expr = inject(new)
            fixed_point = False
            break
    return expr

def relabel_expr(new_labels, expr):
    for old, new in new_labels.iteritems():
        expr = replace_all_in_expr(expr, v_(old), v_(new))
    return expr


