`License <https://github.com/Hasenpfote/malloc_tracer/blob/master/LICENSE>`__
`Build Status <https://travis-ci.org/Hasenpfote/malloc_tracer>`__ `PyPI
version <https://badge.fury.io/py/malloc-tracer>`__
`Pyversions <https://img.shields.io/pypi/pyversions/malloc-tracer.svg?style=flat>`__

malloc_tracer
=============

About
-----

This is a debugging tool for tracing malloc that occurs inside a
function or class.

.. code:: python

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

This is equivalent to the following code.

.. code:: python

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

Feature
-------

Compatibility
-------------

malloc_tracer works with Python 3.4 or higher.

Dependencies
------------

Installation
------------

::

   pip install malloc-tracer

Usage
-----

**Trace a function.**

.. code:: python

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

.. code:: python

   tracer = Tracer(func)
   tracer.trace(
       target_args=dict(x=1, y=2, z=3)
   )

.. figure:: https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage1.png
   :alt: usage1

   usage1

**Trace a method.**

.. code:: python

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

.. code:: python

   instance = Klass(1)
   tracer = Tracer(instance.method)
   tracer.trace(
       target_args=dict(x=1)
   )

.. figure:: https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2a.png
   :alt: usage2a

   usage2a

**Trace a static method.**

.. code:: python

   tracer = Tracer(Klass.smethod)
   tracer.trace(
       target_args=dict()
   )

.. figure:: https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2b.png
   :alt: usage2b

   usage2b

**Trace a class method.**

.. code:: python

   tracer = Tracer(Klass.cmethod)
   tracer.trace(
       target_args=dict(var='Hello world.')
   )

.. figure:: https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2c.png
   :alt: usage2c

   usage2c

**Displays related traces for each file.**

.. code:: python

   import numpy as np
   from malloc_tracer.tracer import *


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

.. code:: python

   tracer = Tracer(func)
   tracer.trace(
       target_args=dict(x=1, y=2, z=3),
       related_traces_output_mode=RelatedTracesOutputMode.FOR_EACH_FILE
   )

.. figure:: https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage3a.png
   :alt: usage3a

   usage3a

**Displays related traces in descending order.**

.. code:: python

   tracer = Tracer(func)
   tracer.trace(
       target_args=dict(x=1, y=2, z=3),
       related_traces_output_mode=RelatedTracesOutputMode.IN_DESCENDING_ORDER
   )

.. figure:: https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage3b.png
   :alt: usage3b

   usage3b

License
-------

This software is released under the MIT License, see LICENSE.
