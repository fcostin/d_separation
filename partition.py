"""
enumeration over all disjoint partitions
"""

def gen_binary_partitions(a):
    if not a:
        yield [[], []]
    else:
        head, tail = a[0], a[1:]
        for u, v in gen_binary_partitions(tail):
            yield [[head] + u, v]
            yield [u, [head] + v]

def gen_partitions(a, k):
    if k == 0:
        yield []
    elif k == 1:
        yield [a]
    elif k == 2:
        for p in gen_binary_partitions(a):
            yield p
    elif k > 2:
        for u, v in gen_binary_partitions(a):
            for p in gen_partitions(v, k - 1):
                yield [u] + p

