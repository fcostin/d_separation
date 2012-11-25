from sitegen import *

def test_gen_v_sites():
    root_expr = prob([v('z')], [v('w'), do(v('x')), do(v('y'))])

    sites = list(gen_v_sites(root_expr))
    assert len(sites) == 1
    target, inject, left, vs, dos = sites[0]
    atom, = target
    assert atom == v('w')
    assert inject('banana') == prob([v('z')], ['banana', do(v('x')), do(v('y'))])
    assert left == (v('z'), )
    assert vs == []
    assert dos == [do(v('x')), do(v('y'))]

def test_gen_do_sites():
    root_expr = prob([v('z')], [v('w'), do(v('x')), do(v('y'))])

    sites = list(gen_do_sites(root_expr))
    assert len(sites) == 2
    target, inject, left, vs, dos = sites[0]
    atom,  = target
    assert atom == do(v('x'))
    assert inject('banana') == prob([v('z')], [v('w'), 'banana', do(v('y'))])
    assert left == (v('z'), )
    assert vs == [v('w')]
    assert dos == [do(v('y'))]

    target, inject, left, vs, dos = sites[1]
    atom,  = target
    assert atom == do(v('y'))
    assert inject('banana') == prob([v('z')], [v('w'), do(v('x')), 'banana'])
    assert left == (v('z'), )
    assert vs == [v('w')]
    assert dos == [do(v('x'))]

