import expr as E
from rules import (RULES, prepare_rule_arguments, bind_arguments)
from graph import Graph

def make_toy_graph():
    vertices = set(['x', 'y', 'z', 'h'])
    edges = set([('h', 'x'), ('x', 'z'), ('z', 'y'), ('h', 'y')])
    return Graph(vertices, edges)


def main():

    graph = make_toy_graph()
   
    # bind variables to subsets of vertices in graph (hack)
    bindings = {
        'z' : set(['z']),
        'x' : set(['x']),
    }

    bind = bindings.get

    root_expr = E.prob([E.v('z')], [E.do(E.v('x'))])

    for rule in RULES:
        print 'considering rule "%s"' % rule['name']
        print '\troot expr:'
        print '\t\t%s' % str(root_expr)
        for site in rule['site_gen'](root_expr):
            print '\ttarget application site:'
            print '\t\t%s' % str(site)
            prepped_args = prepare_rule_arguments(rule['unpack_target'], site)
            bound_args = bind_arguments(bind, prepped_args)
            print '\tbound args:'
            print '\t\t%s' % str(bound_args)
            can_apply = rule['assumption_test'](g = graph, **bound_args)
            print '\tcan apply:'
            print '\t\t%s' % bool(can_apply)
            if can_apply:
                root_expr_prime = rule['apply'](site)
                print '\tresulting expr:'
                print '\t\t%s' % str(root_expr_prime)

        
if __name__ == '__main__':
    main()

