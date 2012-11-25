what is this?

    *   a toy theorem prover for the causal calculus example detailed in Michael Nielsen's article.
    *   probably not anything like an actual theorem prover

what rules does the theorem prover know how to apply?

    *   it can apply the "forwards" versions of the 3 causal calculus rules
    *   it can apply the "reverse" version of the 2nd causal calculus rule
    *   it can condition on things

features/limitations:

    *   it only considers subsets of single vertices
    *   it limits the number of conditioning moves applied to 2 (hack to control search space)
    *   it takes about 8 seconds to prove the example in the article
    *   it uses depth-limited breadth-first search through all proofs wrt the length of the proof


overview of program:

    *   theorem prover
        +   basic idea: breadth-first search on length of proof
        +   state of search is just an expression together with variable bindings
        +   the initial expression and bindings are given as an input
        +   goal is to rewrite the initial expression such that that the result
            -   contains no "do" sub-expressions
            -   does not condition on any specified hidden variables
        +   blindly generate all legal moves and try them, with respect to known rules
        +   known rules
            -   conditioning on a vertex of graph (a random variable)
            -   applying causal calculus rules 1, 2 and 3 in forward direction
            -   applying causal calculus rule 2 in reverse direction
        +   expressions are normalised to avoid redundancy
            -   where order does not matter, sort to normalise
            -   relabel variables based on order in expression

    *   rules
        +   find sites in the expression where we could possibly apply a given rule
        +   test if the assumptions of the rule are met at each possible site
        +   if so, we may apply the rule to produce a new expression

    *   the three causal calculus rules
        +   are applied to prob expressions (expressions are described below)
        +   some rules require the prob to be conditioned on a v, or a do(v)
        +   all rules assume that certain property of causal graph holds
        +   testing these causal graph properties involves simple computations on graphs
        +   the action of these rules when rewriting the expression is simple
        +   these rules may be applied in both "forward" or "reverse" directions
            -   although equality is not directed, expression rewriting is

    *   the conditioning rule
        +   applied to prob expression
        +   rewrites p(x|y,do(z)) with sigma_w p(x|w,y,do(z)) * p(w|x,do(z))
        +   requires a value to be specified to condition on (the index in the sum)
        +   repeated application rapidly grows search space

    *   expressions
        +   expressions are represented as lisp-like expression trees made of tuples
        +   types of expressions:
            -   v : v of variable_name
            -   do : do of v
            -   atom : implicit. either v or do
            -   prob : probability of list of atoms, conditioned on list of atoms
            -   product : product of list of expressions
            -   sigma : sigma of index v and body expression
        +   operations on expressions:
            -   predicates to match expression type
            -   fmt : produces string representation
            -   gen_matches : used to find and rewrite certain sub-expressions
            -   normalise : normalises expressions by sorting lists where possible
            -   filter_map : batch find/replace for expressions. used to relabel variables.

    * graph computations used to check assumptions of causal rules
        +   graph surgery
        +   finding ancestors
        +   d-connectivity test

    *   graph surgery
        +   given
                g : directed acyclic graph
                x : subset of vertices
            chop away all arcs arriving inside x (alternately, departing at x)
        +   simple to compute

    *   finding ancestors
        +   given
                g : directed acyclic graph
                x : subset of vertices
            find the subset of vertices that are ancestors of x
        +   we define all vertices as ancestors of themselves
        +   compute via search

    *   d-connectivity test
        +   given
                g : directed acyclic graph
                x, y, z : subsets of vertices
            determine if the subsets x and y are d-connected
        +   treat as a shortest-path problem; apply Dijkstra
        +   each path tracks the last two arcs traversed and last previous visited
        +   use arcs and prev vertex to determine if prev vertex "blocks" current path
        +   prune blocked paths when growing paths
        +   two subsets are d-connected if they are bridged by an unblocked (shortest) path

    * search
        +   short reusable Dijkstra implementation
        +   can adapt to bfs, dfs, a*
        +   used by d-connection test, ancestors search, and proof search

references:

    http://www.michaelnielsen.org/ddi/if-correlation-doesnt-imply-causation-then-what-does/

