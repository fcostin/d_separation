"""
Dijkstra's algorithm
"""

from heapq import (heappush, heappop)

def search(initial_paths, expand, has_reached_goal, extract_state, verbose=False):
    q = []
    for path in initial_paths:
        heappush(q, path)
    closed = {}
    while q:
        path = heappop(q)
        state = extract_state(path)
        if verbose:
            print '|q| = %d, |closed| = %d' % (len(q), len(closed))
            print 'path = %s' % str(path)

        if state in closed:
            continue
        closed[state] = path
        if has_reached_goal(path):
            return {
                'reached_goal' : True,
                'closed' : closed,
                'path' : path,
            }
        for succ_path in expand(path):
            succ_state = extract_state(succ_path)
            if succ_state in closed:
                continue
            heappush(q, succ_path)
    return {
        'reached_goal' : False,
        'closed' : closed,
        'path' : None,
    }

