#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np


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
