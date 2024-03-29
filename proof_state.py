from util import freeze_dict
from expr import (is_v, unpack_v, gen_matches, normalise_expr, fmt, filter_map, filter_walk)
from expr import v as v_


class ProofState:
    def __init__(self, length, heuristic_length, bindings, root_expr, parent=None, comment=''):
        self.length = length
        self.heuristic_length = heuristic_length
        self.bindings = bindings
        self.root_expr = root_expr
        self.parent = parent
        self.comment = comment
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
            if False: # for debugging
                print '[i=%d], begin...' % i
                print '[i=%d], expr: %s' % (i, str(expr))
                print '[i=%d], expr_prime: %s' % (i, str(expr_prime))
                print '[i=%d], v_order: %s' % (i, str(v_order))
                print '[i=%d], new_labels: %s' % (i, str(new_labels))
                print '[i=%d], bindings_prime: %s' % (i, str(bindings_prime))
                print '[i=%d], expr_prime_prime: %s' % (i, str(expr_prime_prime))
            if expr_prime_prime == expr:
                break
            bindings = bindings_prime
            expr = expr_prime_prime
        return self.copy(bindings=bindings_prime, root_expr=expr_prime_prime)

    def copy(self, **kwargs):
        keys = ['length', 'heuristic_length', 'bindings', 'root_expr', 'parent', 'comment']
        copy_kwargs = {}
        for key in keys:
            copy_kwargs[key] = kwargs.get(key, getattr(self, key))
        return ProofState(**copy_kwargs)

    def extract_state(self):
        # XXX todo freeze bindings
        bindings = freeze_bindings(self.bindings)
        return (bindings, self.root_expr)

    def as_tuple(self):
        return (self.length + self.heuristic_length, ) + self.extract_state()

    def __lt__(self, other):
        return self._tuple < other._tuple

    def __gt(self, other):
        return self._tuple > other._tuple

    def __str__(self):
        total_length = self.length + self.heuristic_length
        return '<ProofState L=%1.1f expr=%s>' % (total_length, fmt(self.root_expr))

# utilities required to normalise the proof state

def get_variable_order(root_expr):
    touched = set()
    order = []
    def f(v):
        if v not in touched:
            touched.add(v)
            order.append(unpack_v(v))
        return v
    # abuse of map - ignore result, just use it to walk tree
    filter_walk(is_v, f, root_expr)
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

def relabel_expr(new_labels, root_expr):
    def p(expr):
        return is_v(expr) and unpack_v(expr) in new_labels
    def f(expr):
        return v_(new_labels[unpack_v(expr)])
    return filter_map(p, f, root_expr)


def freeze_bindings(bindings):
    b = {}
    for k, v in bindings.iteritems():
        b[k] = frozenset(v)
    return freeze_dict(b)

