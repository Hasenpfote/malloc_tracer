`License <https://github.com/Hasenpfote/malloc_tracer/blob/master/LICENSE>`__
`Build Status <https://travis-ci.org/Hasenpfote/malloc_tracer>`__

malloc_tracer
=============

About
-----

This is a debugging tool for tracing malloc that occurs inside a
function or class.

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


   tracer = Tracer(func)
   tracer.trace(
       target_args=dict(x=1, y=2, z=3),
       setup='import numpy as np'
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


   tracer = Tracer(Klass)

   tracer.trace(
       init_args=dict(value=1),
       target_name='method',
       target_args=dict(x=1),
       setup='import numpy as np'
   )

.. figure:: https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2a.png
   :alt: usage2a

   usage2a

**Trace a static method.**

.. code:: python

   # same as above
   tracer.trace(
       target_name='smethod',
       setup='import numpy as np'
   )

.. figure:: https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2b.png
   :alt: usage2b

   usage2b

**Trace a class method.**

.. code:: python

   # same as above
   tracer.trace(
       target_name='cmethod',
       target_args=dict(var='world.'),
   )

.. figure:: https://raw.githubusercontent.com/Hasenpfote/malloc_tracer/master/docs/usage2c.png
   :alt: usage2c

   usage2c

License
-------

This software is released under the MIT License, see LICENSE.
