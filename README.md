[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/Hasenpfote/ malloc_tracer/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/Hasenpfote/malloc_tracer.svg?branch=master)](https://travis-ci.org/Hasenpfote/malloc_tracer)

malloc_tracer
=============

## About
This is a debugging tool for tracing malloc that occurs inside a function or class.  

## Feature

## Compatibility
malloc_tracer works with Python 3.4 or higher.

## Dependencies

## Installation
```
```

## Usage
**Trace a function.**
```python
import numpy as np
from malloc_tracer.tracer import *


def func(x, y, z):
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


tracer = Tracer(func)
tracer.trace(
    target_args=dict(x=1, y=2, z=3),
    setup='import numpy as np'
)
```
![usage1](https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage1.png)

**Trace a method.**
```python
import numpy as np
from malloc_tracer.tracer import *


class Klass(object):

    CONSTANT = 'CONSTANT'

    def __init__(self, value):
        self._value = value

    def method(self, x):
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

    @staticmethod
    def smethod():
        dataset = np.empty((100, ), dtype=np.float64)
        l = [i for i in range(100000)]
        print('Hello')
        return dataset

    @classmethod
    def cmethod(cls, var):
        return cls.CONSTANT + var


tracer = Tracer(Klass)

tracer.trace(
    init_args=dict(value=1),
    target_name='method',
    target_args=dict(x=1),
    setup='import numpy as np'
)
```
![usage2a](https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2a.png)

**Trace a static method.**
```python
# same as above
tracer.trace(
    target_name='smethod',
    setup='import numpy as np'
)
```
![usage2b](https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2b.png)

**Trace a class method.**
```python
# same as above
tracer.trace(
    target_name='cmethod',
    target_args=dict(var='world.'),
)
```
![usage2c](https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2c.png)

## License
This software is released under the MIT License, see LICENSE.
