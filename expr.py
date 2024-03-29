"""
the original plan

    v := ('v', variable_name)
    do := ('do', v)
    atom := do | v
    prob := ('prob', [atom, ...], [atom, ...])
    product := ('product', [expr, ...])
    sigma:= ('sigma', v, expr)

    expr := pr | product | sigma

    bindings := ((variable_name, subset_of_vertices), ...)
    state := (bindings, expr)


claim 1:

    there is a reduction from p(z|do(x)) to p(z|x) using rule 2

    once more with boilerplate:
    start
        bindings = (('z', set([Z_vertex])), ('x', set([X_vertex])))
        expr = prob([v('z')], [do(v('x'))])
    moves
        rule 2
    goal
        bindings = (('z', set([Z_vertex])), ('x', set([X_vertex])))
        expr = prob([v('z')], [v('x')])
"""

from util import (compose, identity)


# define basic expression tree structure

def v(name):
    return ('v', name)

def do(v_):
    return ('do', v_)

def prob(left, right):
    return ('prob', tuple(left), tuple(right))

def product(exprs):
    return ('product', tuple(exprs))

def sigma(v_, expr):
    return ('sigma', v_, expr)



# predicates for case matching

def tag_matches(tag):
    def predicate(expr):
        return expr[0] == tag
    return predicate

is_v = tag_matches('v')
is_do = tag_matches('do')
is_prob = tag_matches('prob')
is_product = tag_matches('product')
is_sigma = tag_matches('sigma')

# a few routines for unpacking vs and dos
def unpack_expr(expr, i=None):
    if i is None:
        i = 1
    return expr[i]

def unpack_v(expr):
    assert is_v(expr)
    return unpack_expr(expr)

def unpack_do(expr):
    assert is_do(expr)
    return unpack_expr(expr)


# define how to ugly-print expressions

def fmt(expr):
    if is_v(expr):
        return str(expr[1])
    elif is_do(expr):
        return 'do(%s)' % fmt(expr[1])
    elif is_prob(expr):
        return 'pr(%s|%s)' % (fmt_list(expr[1]), fmt_list(expr[2]))
    elif is_product(expr):
        return 'product(%s)' % fmt_list(expr[1])
    elif is_sigma(expr):
        return 'sigma(%s, %s)' % (fmt(expr[1]), fmt(expr[2]))

def fmt_list(exprs):
    return ','.join(map(fmt, exprs))

# machinery for find/replacing sub-expressions of expression trees

def gen_matches(predicate, expr, inject=None):
    if inject is None:
        inject = lambda x : x
    # do we match?
    if predicate(expr):
        yield expr, inject

    # recursively generate all matches in child expressions
    # n.b. there is a lot of redundancy here that could be cleaned up
    # by defining these operations for tuples and lists (hey, both of
    # those cases are essentially the same...)
    if is_v(expr):
        return
    elif is_do(expr):
        next_expr = expr[1]
        next_inject = compose(inject, do)
        for result in gen_matches(predicate, next_expr, next_inject):
            yield result
    elif is_prob(expr):
        left, right = expr[1], expr[2]
        for i, next_expr in enumerate(left):
            iota = make_list_inject(i, left)
            prob_inject = make_left_inject('prob', iota, right)
            next_inject = compose(inject, prob_inject)
            for result in gen_matches(predicate, next_expr, next_inject):
                yield result
        for i, next_expr in enumerate(right):
            iota = make_list_inject(i, right)
            prob_inject = make_right_inject('prob', left, iota)
            next_inject = compose(inject, prob_inject)
            for result in gen_matches(predicate, next_expr, next_inject):
                yield result
    elif is_product(expr):
        children = expr[1]
        for i, next_expr in enumerate(children):
            iota = make_list_inject(i, children)
            product_inject = make_unary_inject('product', iota)
            next_inject = compose(inject, product_inject)
            for result in gen_matches(predicate, next_expr, next_inject):
                yield result
    elif is_sigma(expr):
        left, right = expr[1], expr[2]
        # left case (replace index var)
        next_expr = left
        sigma_inject = make_left_inject('sigma', identity, right)
        next_inject = compose(inject, sigma_inject)
        for result in gen_matches(predicate, next_expr, next_inject):
            yield result
        # right case (replace body expr)
        next_expr = right
        sigma_inject = make_right_inject('sigma', left, identity)
        next_inject = compose(inject, sigma_inject)
        for result in gen_matches(predicate, next_expr, next_inject):
            yield result

def make_list_inject(i, a):
    def list_inject(x=None, drop=False):
        if drop:
            body = ()
        else:
            body = (x, )
        return tuple(a[:i]) + body + tuple(a[i+1:])
    return list_inject

def make_left_inject(tag, iota, right):
    def inject(*args, **kwargs):
        return (tag, iota(*args, **kwargs), right)
    return inject

def make_right_inject(tag, left, iota):
    def inject(*args, **kwargs):
        return (tag, left, iota(*args, **kwargs))
    return inject

def make_unary_inject(tag, iota):
    def inject(*args, **kwargs):
        return (tag, iota(*args, **kwargs))
    return inject

# machinery for normalising things

def normalise_expr(expr):
    if is_v(expr):
        return expr
    elif is_do(expr):
        return expr
    elif is_prob(expr):
        return normalise_prob(expr)
    elif is_product(expr):
        return normalise_product(expr)
    elif is_sigma(expr):
        return normalise_sigma(expr)
    raise ValueError(expr)

def normalise_expr_list(exprs):
    """this is the only normalisation function that actually does anything!"""
    return tuple(sorted(map(normalise_expr, exprs)))

def normalise_prob(expr):
    return (expr[0], normalise_expr_list(expr[1]), normalise_expr_list(expr[2]))

def normalise_product(expr):
    return (expr[0], normalise_expr_list(expr[1]))

def normalise_sigma(expr):
    return (expr[0], normalise_expr(expr[1]), normalise_expr(expr[2]))


# a single pass combined filter-map.
# it doesn't actually filter. it acts like identity where predicate is false.
# heh.

def filter_map(predicate, f, root_expr):

    def _filter_map(expr):
        if predicate(expr):
            return f(expr)
        elif is_v(expr):
            return v(expr)
        elif is_do(expr):
            return do(_filter_map(expr[1]))
        elif is_prob(expr):
            return prob(_filter_map_exprs(expr[1]), _filter_map_exprs(expr[2]))
        elif is_product(expr):
            return product(_filter_map_exprs(expr[1]))
        elif is_sigma(expr):
            return sigma(_filter_map(expr[1]), _filter_map(expr[2]))

    def _filter_map_exprs(exprs):
        return tuple(_filter_map(expr) for expr in exprs)

    return _filter_map(root_expr)

def filter_walk(predicate, f, root_expr):

    def _filter_walk(expr):
        if predicate(expr):
            f(expr)
        elif is_do(expr):
            _filter_walk(expr[1])
        elif is_prob(expr):
            _filter_walk_exprs(expr[1])
            _filter_walk_exprs(expr[2])
        elif is_product(expr):
            _filter_walk_exprs(expr[1])
        elif is_sigma(expr):
            _filter_walk(expr[1])
            _filter_walk(expr[2])

    def _filter_walk_exprs(exprs):
        for expr in exprs:
            _filter_walk(expr)

    _filter_walk(root_expr)

