from expr import (v, do, prob, product, sigma)
from proof_state import ProofState

def test_normalise_single_iter():
    root_expr = sigma(v('x'), product([prob([v('z'), v('y')], [v('b'), v('x'), do(v('a'))]),
        prob([v('z'), v('y'), v('x')], [do(v('a'))])]))

    bindings = {'x' : 'xxx', 'z' : 'zzz', 'y' : 'yyy', 'a' : 'aaa'}

    state = ProofState(0, 0, bindings, root_expr)

    normalised_state = state.normalise(max_iters=1)

    # first up: expression ordering (nb do(v()) comes before v() in sorted lists)
    # sigma(x, product([prob([x y z],[do(a)]), prob([y z], [(do a) b x])]))
    # so, variable order should be:
    # x y z a b
    # so, new variable names should be
    # 0 1 2 3 4
    # so, normalised state should be
    # sigma(0, product([prob([0 1 2],[do(3)]), prob([1 2], [(do 3) 4 0])]))

    expected_result = sigma(v(0), product((prob((v(0), v(1), v(2)),(do(v(3)), )),
        prob((v(1), v(2)), (do(v(3)), v(4), v(0))))))

    assert normalised_state.root_expr == expected_result

def test_normalise_fixed_point():
    root_expr = sigma(v('x'), product([prob([v('z'), v('y')], [v('b'), v('x'), do(v('a'))]),
        prob([v('z'), v('y'), v('x')], [do(v('a'))])]))

    bindings = {'x' : 'xxx', 'z' : 'zzz', 'y' : 'yyy', 'a' : 'aaa'}

    state = ProofState(0, 0, bindings, root_expr)

    normalised_state = state.normalise()

    expected_result = sigma(v(0), product((prob((v(0), v(1), v(2)),(do(v(3)), )),
        prob((v(1), v(2)), (do(v(3)), v(0), v(4))))))

    assert normalised_state.root_expr == expected_result


