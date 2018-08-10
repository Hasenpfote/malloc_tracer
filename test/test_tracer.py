#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math as mathematics  # Avoid conflict with the tracer module.
import contextlib
from unittest import TestCase
import sys
sys.path.append('../')
from malloc_tracer.tracer import *


def function(base, num):
    l = [mathematics.pow(base, i) for i in range(num)]
    return l


def function2(base=mathematics.e):
    return mathematics.pow(base, 2)


class Klass(object):

    CONSTANT = 10

    def __init__(self, base, num):
        self.base = base
        self.num = num

    def method(self):
        l = [mathematics.pow(self.base, i) for i in range(self.num)]
        return l

    @staticmethod
    def smethod(base, num):
        l = [mathematics.pow(base, i) for i in range(num)]
        return l

    @classmethod
    def cmethod(cls, base):
        return mathematics.pow(base, cls.CONSTANT)


class Klass2(object):

    CONSTANT = 10

    def method(self, base=mathematics.e, num=10):
        l = [mathematics.pow(base, i) for i in range(num)]
        return l

    @staticmethod
    def smethod(base=mathematics.e, num=10):
        l = [mathematics.pow(base, i) for i in range(num)]
        return l

    @classmethod
    def cmethod(cls, base=mathematics.e):
        return mathematics.pow(base, cls.CONSTANT)


class TestTracer(TestCase):

    def test_function(self):
        tracer = Tracer(
            function,
            enable_auto_resolve=False
        )
        with contextlib.redirect_stdout(None):
            tracer.trace(
                target_args=dict(base=2, num=100),
                setup='import math as mathematics'
            )

    def test_function_with_default_args(self):
        tracer = Tracer(
            function2,
            enable_auto_resolve=False,
            setup='import math as mathematics'
        )
        with contextlib.redirect_stdout(None):
            tracer.trace(
                setup='import math as mathematics'
            )

    def test_function_with_auto_resolve_dependencies(self):
        tracer = Tracer(
            function2,
            enable_auto_resolve=True
        )
        with contextlib.redirect_stdout(None):
            tracer.trace()

    def test_method(self):
        instance = Klass(2, 100)
        tracer = Tracer(
            instance.method,
            enable_auto_resolve=False
        )
        with contextlib.redirect_stdout(None):
            tracer.trace(
                setup='import math as mathematics'
            )

    def test_method_with_default_args(self):
        instance = Klass2()
        tracer = Tracer(
            instance.method,
            enable_auto_resolve=False,
            setup='import math as mathematics'
        )
        with contextlib.redirect_stdout(None):
            tracer.trace(
                setup='import math as mathematics'
            )

    def test_method_with_auto_resolve_dependencies(self):
        instance = Klass2()
        tracer = Tracer(
            instance.method,
            enable_auto_resolve=True
        )
        with contextlib.redirect_stdout(None):
            tracer.trace()

    def test_static_method(self):
        tracer = Tracer(
            Klass.smethod,
            enable_auto_resolve=False
        )
        with contextlib.redirect_stdout(None):
            tracer.trace(
                target_args=dict(base=2, num=100),
                setup='import math as mathematics'
            )

    def test_static_method_with_default_args(self):
        tracer = Tracer(
            Klass2.smethod,
            enable_auto_resolve=False,
            setup='import math as mathematics'
        )
        with contextlib.redirect_stdout(None):
            tracer.trace(
                target_args=dict(base=2, num=100),
                setup='import math as mathematics'
            )

    def test_static_method_with_auto_resolve_dependencies(self):
        tracer = Tracer(
            Klass2.smethod,
            enable_auto_resolve=True
        )
        with contextlib.redirect_stdout(None):
            tracer.trace(
                target_args=dict(base=2, num=100),
            )

    def test_class_method(self):
        tracer = Tracer(
            Klass.cmethod,
            enable_auto_resolve=False
        )
        with contextlib.redirect_stdout(None):
            tracer.trace(
                target_args=dict(base=1),
                setup='import math as mathematics',
            )

    def test_class_method_with_default_args(self):
        tracer = Tracer(
            Klass2.cmethod,
            enable_auto_resolve=False,
            setup='import math as mathematics'
        )
        with contextlib.redirect_stdout(None):
            tracer.trace(
                target_args=dict(base=1),
                setup='import math as mathematics',
            )

    def test_class_method_with_auto_resolve_dependencies(self):
        tracer = Tracer(
            Klass2.cmethod,
            enable_auto_resolve=True
        )
        with contextlib.redirect_stdout(None):
            tracer.trace(
                target_args=dict(base=1),
            )
