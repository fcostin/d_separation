a toy theorem prover for causal calculus
----------------------------------------

### This is

*   a toy theorem prover for the causal calculus example detailed in Michael Nielsen's article.
*   probably not anything like an actual theorem prover

### Example output:

    step 0
        comment:
            initial state
        expr:
            pr(y|do(x))
    step 1
        comment:
            conditioned pr(y|do(x)) on z
        expr:
            sigma(z, product(pr(z|do(x)),pr(y|do(x),z)))
    step 2
        comment:
            applied rule ignore_intervention_act_reverse to pr(y|do(x),z)
        expr:
            sigma(z, product(pr(z|do(x)),pr(y|do(z),do(x))))
    step 3
        comment:
            applied rule ignore_intervention_entirely_forward to pr(y|do(z),do(x))
        expr:
            sigma(z, product(pr(z|do(x)),pr(y|do(z))))
    step 4
        comment:
            conditioned pr(y|do(z)) on x
        expr:
            sigma(z, product(pr(z|do(x)),sigma(x', product(pr(x'|do(z)),pr(y|do(z),x')))))
    step 5
        comment:
            applied rule ignore_intervention_act_forward to pr(y|do(z),x')
        expr:
            sigma(z, product(pr(z|do(x)),sigma(x', product(pr(x'|do(z)),pr(y|z,x')))))
    step 6
        comment:
            applied rule ignore_intervention_act_forward to pr(z|do(x))
        expr:
            sigma(z, product(pr(z|x),sigma(x', product(pr(x'|do(z)),pr(y|z,x')))))
    step 7
        comment:
            applied rule ignore_intervention_entirely_forward to pr(x'|do(z))
        expr:
            sigma(z, product(pr(z|x),sigma(x', product(pr(x'|),pr(y|z,x')))))

### What rules does the theorem prover know how to apply?

*   it can apply the "forwards" versions of the three causal calculus rules
*   it can apply the "reverse" version of the second causal calculus rule
*   it can also condition on variables

### Features/limitations:

*   it only considers subsets of single vertices
*   it limits the number of conditioning moves applied to 2 (this is a hack to control search space)
*   it takes about 0.2 seconds to prove the example in the article using a greedy heuristic (!)
*   it uses a depth-limited breadth-first search to search all proofs wrt the length of the proof


### Construction:

*   the theorem prover
    +   basic idea: breadth-first search on length of proof
    +   state of search is just an expression together with variable bindings
    +   the initial expression and bindings are given as an input
    +   the goal is to rewrite the initial expression such that that the result:
        -   contains no "do" sub-expressions
        -   does not condition on any specified hidden variables
    +   blindly generate all legal moves and try them, with respect to known rules
    +   now uses greedy heuristic to attract search toward promising-looking expressions
    +   known rules:
        -   conditioning on a vertex of graph (a random variable)
        -   applying causal calculus rules 1, 2 and 3 in forward direction
        -   applying causal calculus rule 2 in reverse direction
    +   expressions are normalised to avoid redundancy:
        -   where order does not matter, sort to normalise
        -   relabel variables based on order in expression

*   rules
    +   find sites in the expression where we could possibly apply a given rule
    +   test if the assumptions of the rule are met at each possible site
    +   if so, we may apply the rule to produce a new expression

*   the three causal calculus rules
    +   are applied to `prob` expressions (expressions are described below)
    +   some rules require the `prob` to be conditioned on a v, or a do(v)
    +   all rules assume that certain property of causal graph holds
    +   testing these causal graph properties involves computations on graphs
    +   the action of these rules is to rewrite expressions
    +   these rules may be applied in both "forward" or "reverse" directions
        -   although equality is not directed, expression rewriting is

*   the conditioning rule
    +   applied to `prob` expression
    +   rewrites `p(x|y,do(z))` as `sigma_w p(x|w,y,do(z)) * p(w|x,do(z))`
    +   requires a value to be specified to condition on (the index in the sum)
    +   repeated application rapidly grows search space

*   expressions
    +   expressions are represented as lisp-like expression trees made of tuples
    +   types of expressions:
        -   `v` : `v` of `variable_name`, represents a variable
        -   `do` : `do` of `v`
        -   `atom` : implicit. either a `v` or a `do`
        -   `prob` : probability of list of `atom`s, conditioned on list of `atom`s
        -   `product` : product of list of `expression`s
        -   `sigma` : `sigma` of index `v` and body `expression`
    +   operations on expressions:
        -   predicates to match expression type
        -   `fmt` : produces string representation
        -   `gen_matches` : used to find and rewrite certain sub-expressions
        -   `normalise` : normalises expressions by sorting lists where possible
        -   `filter_map` : batch find/replace for expressions. used to relabel variables.

*   graph computations used to check assumptions of causal rules
    +   graph surgery
    +   finding ancestors
    +   d-connectivity test

*   graph surgery
    +   given
            directed acyclic graph `g` and
            subset of vertices `x`,
            chop away all arcs arriving inside `x`.
    +   one variation is to do the same for all arcs departing `x`

*   finding ancestors
    +   given
            directed acyclic graph `g` and
            subset of vertices `x`
        find the subset of vertices that are ancestors of `x`
    +   we define all vertices as ancestors of themselves
    +   find ancestors via search

*   d-connectivity test
    +   given
            directed acyclic graph `g` and
            three subset of vertices `x`, `y` and `z`,
        determine if the subsets `x` and `y` are d-connected given `z`.
    +   treat as a shortest-path problem; apply Dijkstra
    +   each path tracks the last two arcs traversed and last previous visited
    +   use arcs and prev vertex to determine if prev vertex "blocks" current path
    +   prune blocked paths when growing paths
    +   two subsets are d-connected if they are bridged by an unblocked (shortest) path

* search
    +   short reusable Dijkstra implementation
    +   can adapt to bfs, dfs, `A*`
    +   used by d-connection test, ancestors search, and proof search

### References:

1.  http://www.michaelnielsen.org/ddi/if-correlation-doesnt-imply-causation-then-what-does/

