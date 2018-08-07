#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import contextlib
from unittest import TestCase
import sys
sys.path.append('../')
from malloc_tracer.tracer import *


def function(base, num):
    l = [math.pow(base, i) for i in range(num)]
    return l


class Klass(object):
    def __init__(self, base, num):
        self.base = base
        self.num = num

    def method(self):
        l = [math.pow(self.base, i) for i in range(self.num)]
        return l

    @staticmethod
    def smethod(base, num):
        l = [math.pow(base, i) for i in range(num)]
        return l


class TestTracer(TestCase):

    def test_function(self):
        tracer = Tracer(function)
        with contextlib.redirect_stdout(None):
            tracer.trace(
                target_args=dict(base=2, num=100),
                setup='import math'
            )
            tracer.trace(
                target_args=dict(base=2, num=100),
                setup='import math',
                verbose=True
            )

    def test_method(self):
        tracer = Tracer(Klass)
        with contextlib.redirect_stdout(None):
            tracer.trace(
                init_args=dict(base=2, num=100),
                target_name='method',
                setup='import math'
            )
            tracer.trace(
                init_args=dict(base=2, num=100),
                target_name='method',
                setup='import math',
                verbose=True
            )

    def test_static_method(self):
        tracer = Tracer(Klass)
        with contextlib.redirect_stdout(None):
            tracer.trace(
                target_name='smethod',
                target_args=dict(base=2, num=100),
                setup='import math'
            )
            tracer.trace(
                target_name='smethod',
                target_args=dict(base=2, num=100),
                setup='import math',
                verbose=True
            )
