[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/Hasenpfote/malloc_tracer/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/Hasenpfote/malloc_tracer.svg?branch=master)](https://travis-ci.org/Hasenpfote/malloc_tracer)
[![PyPI version](https://badge.fury.io/py/malloc-tracer.svg)](https://badge.fury.io/py/malloc-tracer)
[![Pyversions](https://img.shields.io/pypi/pyversions/malloc-tracer.svg?style=flat)](https://img.shields.io/pypi/pyversions/malloc-tracer.svg?style=flat)

malloc_tracer
=============

## About
This is a debugging tool for tracing malloc that occurs inside a function or class.  

```python
import numpy as np
import malloc_tracer


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


tracer = malloc_tracer.Tracer(func)
```

This is equivalent to the following code.

```python
import numpy as np
from tracemalloc import start, take_snapshot, stop


SNAPSHOT = None


def func(x, y, z):
    try:
        start()
        dataset1 = np.empty((100,), dtype=np.float64)
        print('x', x)
        dataset1 = np.empty((1000,), dtype=np.float64)

        l = [i for i in range(100000)]

        if (x == 0):
            dataset4a = np.empty((100000,), dtype=np.float64)
            return 0
        elif (x == 1):
            dataset4b = np.empty((100000,), dtype=np.float64)
            return 1

        dataset3 = np.empty((3000,), dtype=np.float64)
        return 2
    finally:
        global SNAPSHOT
        SNAPSHOT = take_snapshot()
        stop()
```

## Feature

## Compatibility
malloc_tracer works with Python 3.4 or higher.

## Dependencies

## Installation
```
pip install malloc-tracer
```

## Usage
**Trace a function.**
```python
import numpy as np
import malloc_tracer


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
```

```python
tracer = malloc_tracer.Tracer(func)
tracer.trace(
    target_args=dict(x=1, y=2, z=3)
)
```
![usage1](https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage1.png)

**Trace a method.**
```python
import numpy as np
import malloc_tracer


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
```

```python
instance = Klass(1)
tracer = malloc_tracer.Tracer(instance.method)
tracer.trace(
    target_args=dict(x=1)
)
```
![usage2a](https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2a.png)

**Trace a static method.**
```python
tracer = malloc_tracer.Tracer(Klass.smethod)
tracer.trace(
    target_args=dict()
)
```
![usage2b](https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2b.png)

**Trace a class method.**
```python
tracer = malloc_tracer.Tracer(Klass.cmethod)
tracer.trace(
    target_args=dict(var='Hello world.')
)
```
![usage2c](https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2c.png)

**Displays related traces for each file.**
```python
import numpy as np
import malloc_tracer


global_var1 = None
global_var2 = None


def func2():
    global global_var1
    global global_var2
    global_var1 = np.empty((1000, ), dtype=np.float64)
    global_var2 = np.empty((10000, ), dtype=np.float64)


def func(x, y, z):
    dataset1 = np.empty((100, ), dtype=np.float64)
    print('x', x)
    dataset1 = np.empty((1000, ), dtype=np.float64)

    l = [i for i in range(100000)]

    func2()

    if x == 0:
        dataset4a = np.empty((100000, ), dtype=np.float64)
        return 0
    elif x == 1:
        dataset4b = np.empty((100000, ), dtype=np.float64)
        return 1

    dataset3 = np.empty((3000, ), dtype=np.float64)
    return 2
```

```python
tracer = malloc_tracer.Tracer(func)
tracer.trace(
    target_args=dict(x=1, y=2, z=3),
    related_traces_output_mode=malloc_tracer.RelatedTracesOutputMode.FOR_EACH_FILE
)
```
![usage3a](https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage3a.png)

**Displays related traces in descending order.**
```python
tracer = malloc_tracer.Tracer(func)
tracer.trace(
    target_args=dict(x=1, y=2, z=3),
    related_traces_output_mode=malloc_tracer.RelatedTracesOutputMode.IN_DESCENDING_ORDER
)
```
![usage3b](https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage3b.png)

**Convenience function.**
```python
malloc_tracer.trace(
    func,
    target_args=dict(x=1, y=2, z=3),
    related_traces_output_mode=malloc_tracer.RelatedTracesOutputMode.IN_DESCENDING_ORDER
)
```

## License
This software is released under the MIT License, see LICENSE.
