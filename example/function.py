#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.getcwd())
sys.path.append('../')
import foo
from malloc_tracer.tracer import *


def main():
    tracer = Tracer(foo.func)
    tracer.trace(
        target_args=dict(x=1, y=2, z=3)
    )


if __name__ == '__main__':
    main()
