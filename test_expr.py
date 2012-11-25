from expr import *

def test_fmt():
    root_expr = prob([v('z')], [do(v('x'))])
    assert fmt(root_expr) == 'pr(z|do(x))'

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

def test_gen_matches_deep():
    # sigma_y { p(x|y,do(z)) * p(y|do(z)) }
    root_expr = sigma(v('y'), product([prob([v('x')], [v('y'), do(v('z'))]),
        prob([v('y')], [do(v('z'))])]))

    matches = list(gen_matches(is_v, root_expr))
    assert len(matches) == 6

    expr, inject = matches[3]
    assert expr == v('z')

    root_expr_prime = inject('walrus')
    assert root_expr_prime == sigma(v('y'), product([prob([v('x')], [v('y'), do('walrus')]),
        prob([v('y')], [do(v('z'))])]))

