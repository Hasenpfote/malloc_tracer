import numpy as np
from malloc_tracer.tracer import *


def function(x, y, z):
    dataset1 = np.empty((100, ), dtype=np.float64)
    print('x', x)
    dataset1 = np.empty((1000, ), dtype=np.float64)

    l = [i for i in range(100000)]

    if x == 0:
        dataset4a = np.empty((100000, ), dtype=np.float64)
        return 0
    elif x == 1:
        dataset4b = np.empty((100000, ), dtype=np.float64)
        return 1

    dataset3 = np.empty((3000, ), dtype=np.float64)
    return 2


# Test for function.
def test1():
    tracer = Tracer(function)
    tracer.trace(
        target_args=dict(x=1, y=2, z=3),
        setup='import numpy as np'
    )


def main():
    test1()


if __name__ == '__main__':
    main()
