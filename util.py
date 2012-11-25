def identity(x):
    return x

def without(i, a):
    return a[:i] + a[(i+1):]

def compose(f, g):
    def f_g(*args, **kwargs):
        return f(g(*args, **kwargs))
    return f_g

