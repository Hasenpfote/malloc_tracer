#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.getcwd())
sys.path.append('../')
import bar
import malloc_tracer


def main():
    print(malloc_tracer.__version__)

    instance = bar.Klass(value=1)
    tracer = malloc_tracer.Tracer(instance.method)
    tracer.trace(
        target_args=dict(x=1),
    )

    tracer = malloc_tracer.Tracer(bar.Klass.smethod)
    tracer.trace()

    tracer = malloc_tracer.Tracer(bar.Klass.cmethod)
    tracer.trace(
        target_args=dict(var='world.'),
    )


if __name__ == '__main__':
    main()
