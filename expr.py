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


# define basic expression tree structure

def v(name):
    return ('v', name)

def do(v):
    return ('do', v)

def prob(left, right):
    return ('prob', list(left), list(right))

def product(exprs):
    return ('product', list(exprs))

def sigma(v, expr):
    return ('sigma', v, expr)



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



# define how to ugly-print expressions

def fmt(expr):
    if is_v(expr):
        return expr[1]
    elif is_do(expr):
        return 'do(%s)' % fmt(expr[1])
    elif is_prob(expr):
        return 'pr(%s|%s)' % (fmt_list(expr[1]), fmt_list(expr[2]))
    elif is_product(expr):
        return 'product{%s}' % fmt_list(expr[1])
    elif is_sigma(expr):
        return 'sigma(%s){%s}' % (fmt(expr[1]), fmt(expr[2]))

def fmt_list(exprs):
    return ','.join(map(fmt, exprs))

def test_fmt():
    root_expr = prob([v('z')], [do(v('x'))])
    assert fmt(root_expr) == 'pr(z|do(x))'



# machinery for find/replacing sub-expressions of expression trees

def gen_matches(predicate, expr, inject=None):
    if inject is None:
        inject = lambda x : x
    # do we match?
    if predicate(expr):
        yield expr, inject
    # recursively generate all matches in child expressions
    tag = expr[0]

    # n.b. there is a lot of redundancy here that could be cleaned up
    # by defining these operations for tuples and lists (hey, both of
    # those cases are essentially the same...)
    if is_v(expr):
        return
    elif is_do(expr):
        next_expr = expr[1]
        next_inject = lambda v : inject(do(v))
        for result in gen_matches(predicate, next_expr, next_inject):
            yield result
    elif is_prob(expr):
        for i, next_expr in enumerate(expr[1]):
            iota = make_list_inject(i, expr[1])
            next_inject = lambda x : prob(iota(x), expr[2])
            for result in gen_matches(predicate, next_expr, next_inject):
                yield result
        for i, next_expr in enumerate(expr[2]):
            iota = make_list_inject(i, expr[2])
            next_inject = lambda x : prob(expr[1], iota(x))
            for result in gen_matches(predicate, next_expr, next_inject):
                yield result
    elif is_product(expr):
        for i, next_expr in enumerate(expr[1]):
            iota = make_list_inject(i, expr[1])
            next_inject = lambda x : product(iota(x))
            for result in gen_matches(predicate, next_expr, next_inject):
                yield result
    elif is_sigma(expr):
        next_expr = expr[1]
        next_inject = lambda x : sigma(x, expr[2])
        for result in gen_matches(predicate, next_expr, next_inject):
            yield result
        for i, next_expr in enumerate(expr[2]):
            iota = make_list_inject(i, expr[2])
            next_inject = lambda x : sigma(expr[1], iota(x))
            for result in gen_matches(predicate, next_expr, next_inject):
                yield result

def make_list_inject(i, a):
    def list_inject(x):
        return list(a[:i]) + [x] + list(a[i+1:])
    return list_inject

def test_gen_matches():
    root_expr = prob([v('z')], [do(v('x'))])

    matches = list(gen_matches(is_v, root_expr))
    assert len(matches) == 2
    match_a, match_b = matches
    assert match_a[0] == v('z')
    assert match_b[0] == v('x')

    # test substitution machinery
    assert match_a[1]('banana') == prob(['banana'], [do(v('x'))])
    assert match_b[1]('rambutan') == prob([v('z')], [do('rambutan')])

