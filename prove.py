import logging

import expr as E
from util import (identity, set_union)
from main import (make_toy_graph, ignore_observations_assumption,
    ignore_intervention_act_assumption,
    ignore_intervention_entirely_assumption)
from sitegen import (gen_do_sites, gen_v_sites, gen_birth_sites)

def prepare_rule_arguments(unpack_target, site):
    """
    arguments
        unpack_target : function s.t. map(unpack_target, target) is [variable, ...]
        site : (target, inject, left, vs, dos)
    return value:
        args : {arg_name : [variable, ...], ...}
    """
    target, inject, left, vs, dos = site
    return {
        'x' : map(E.unpack_do, dos),
        'y' : left,
        'z' : map(unpack_target, target),
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


def apply_ignore_observations_forward(site):
    inject = site[1]
    return inject(drop=True)

def apply_ignore_observations_reverse(site):
    # XXX this makes a v(...) out of nothing,
    # so it needs to be parametrised by which v(...) to make.
    # this suggests parametric rules are required. ignore
    # that for now.
    logging.warn('apply ignore observations reverse isnt implemented; doing identity')
    inject = site[1]
    return inject(drop=True) # XXX replace this with inject(v)


def apply_ignore_intervention_act_forward(site):
    target, inject = site[:2]
    atom, = target
    v = E.unpack_do(atom)
    return inject(v)

def apply_ignore_intervention_act_reverse(site):
    target, inject = site[:2]
    v, = target
    return inject(E.do(v))

def apply_ignore_intervention_entirely_forward(site):
    inject = site[1]
    return inject(drop=True)

def apply_ignore_intervention_entirely_reverse(site):
    # XXX this makes a do(v(...)) out of nothing,
    # so it needs to be parametrised by which do(v(...)) to make.
    # this suggests parametric rules are required. ignore
    # that for now.
    logging.warn('apply ignore intervention entirely reverse isnt implemented; doing identity')
    inject = site[1]
    return inject(drop=True) # XXX replace this with inject(v)




RULES = [
    {
        'name' : 'ignore_observations_forward',
        'site_gen' : gen_v_sites,
        'unpack_target' : identity,
        'assumption_test' : ignore_observations_assumption,
        'apply' : apply_ignore_observations_forward,
    },
    {
        'name' : 'ignore_observations_reverse',
        'site_gen' : gen_birth_sites,
        'unpack_target' : identity,
        'assumption_test' : ignore_observations_assumption,
        'apply' : apply_ignore_observations_reverse,
    },
    {
        'name' : 'ignore_intervention_act_forward',
        'site_gen' : gen_do_sites,
        'unpack_target' : E.unpack_do,
        'assumption_test' : ignore_intervention_act_assumption,
        'apply' : apply_ignore_intervention_act_forward,
    },
    {
        'name' : 'ignore_intervention_act_reverse',
        'site_gen' : gen_v_sites,
        'unpack_target' : identity,
        'assumption_test' : ignore_intervention_act_assumption,
        'apply' : apply_ignore_intervention_act_reverse,
    },
    {
        'name' : 'ignore_intervention_entirely_forward',
        'site_gen' : gen_do_sites,
        'unpack_target' : E.unpack_do,
        'assumption_test' : ignore_intervention_entirely_assumption,
        'apply' : apply_ignore_intervention_entirely_forward,
    },
    {
        'name' : 'ignore_intervention_entirely_reverse',
        'site_gen' : gen_birth_sites,
        'unpack_target' : identity,
        'assumption_test' : ignore_intervention_entirely_assumption,
        'apply' : apply_ignore_intervention_entirely_reverse,
    },
]



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

