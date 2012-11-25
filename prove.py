import expr as E

from util import (set_union)
from main import (make_toy_graph, ignore_intervention_act_assumption)
from sitegen import (gen_do_sites)

def prepare_rule_arguments(site):
    """
    arguments
        site : (target, inject, left, vs, dos)
    return value:
        args : {arg_name : [variable, ...], ...}
    """
    target, inject, left, vs, dos = site
    return {
        'x' : map(E.unpack_do, dos),
        'y' : left,
        'z' : map(E.unpack_do, target),
        'w' : vs,
    }

def bind_arguments(bind, args):
    """
    arguments:
        bind : function variable -> vertex set
        args : {arg_name : [variable, ...], ...}
    return value:
        bound_args : {arg_name : vertex set, ...}
    """

    result = {}
    for arg_name, v_exprs in args.iteritems():
        symbols = map(E.unpack_v, v_exprs)
        subsets = map(bind, symbols)
        result[arg_name] = set_union(subsets)
    return result


def main():

    graph = make_toy_graph()
   
    # bind variables to subsets of vertices in graph (hack)
    bindings = {
        'z' : set(['z']),
        'x' : set(['x']),
    }

    bind = bindings.get

    root_expr = E.prob([E.v('z')], [E.do(E.v('x'))])

    for site in gen_do_sites(root_expr):
        print 'potential rule application:'
        print '\troot expr:'
        print '\t\t%s' % str(root_expr)
        print '\ttarget application site:'
        print '\t\t%s' % str(site)
        prepped_args = prepare_rule_arguments(site)
        bound_args = bind_arguments(bind, prepped_args)
        print '\tbound args:'
        print '\t\t%s' % str(bound_args)

        can_apply = ignore_intervention_act_assumption(g = graph, **bound_args)
        print '\tcan apply:'
        print '\t\t%s' % str(can_apply)

        if can_apply:
            target, inject = site[:2]
            atom, = target
            v = E.unpack_do(atom)
            root_expr_prime = inject(v)
        
            print '\tresulting expr:'
            print '\t\t%s' % str(root_expr_prime)
        
if __name__ == '__main__':
    main()

