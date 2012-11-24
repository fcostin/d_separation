"""
Dijkstra's algorithm
"""

from heapq import (heappush, heappop)

def search(initial_paths, expand, has_reached_goal, extract_state):
    q = []
    for path in initial_paths:
        heappush(q, paths)
    closed = {}
    while q:
        path = heappop(q)
        state = extract_state(path)
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

