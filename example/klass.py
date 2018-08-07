#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.getcwd())
sys.path.append('../')
import bar
from malloc_tracer.tracer import *


def main():
    tracer = Tracer(bar.Klass)

    tracer.trace(
        init_args=dict(value=1),
        target_name='method',
        target_args=dict(x=1),
        setup='import numpy as np'
    )

    tracer.trace(
        target_name='smethod',
        setup='import numpy as np'
    )

    tracer.trace(
        target_name='cmethod',
        target_args=dict(var='world.'),
    )


if __name__ == '__main__':
    main()
