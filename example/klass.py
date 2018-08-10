#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.getcwd())
sys.path.append('../')
import bar
from malloc_tracer.tracer import *


def main():
    instance = bar.Klass(value=1)
    tracer = Tracer(instance.method)
    tracer.trace(
        target_args=dict(x=1),
    )

    tracer = Tracer(bar.Klass.smethod)
    tracer.trace()

    tracer = Tracer(bar.Klass.cmethod)
    tracer.trace(
        target_args=dict(var='world.'),
    )


if __name__ == '__main__':
    main()
