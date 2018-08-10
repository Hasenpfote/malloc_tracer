#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import ast
import math
import contextlib
import textwrap
from tracemalloc import start, take_snapshot, stop, Filter


__all__ = ['Tracer', ]


DUMMY_SRC_NAME = '<tracer-src>'


def bytes_to_hrf(size):
    '''Convert bytes to human readable format.'''
    units = ('B', 'KiB', 'MiB', 'GiB', 'TiB')

    if size > 0:
        order = min(int(math.log(size) / math.log(1024)), len(units)-1)
    else:
        order = 0

    fmt = '6.0f' if order == 0 else '6.1f'
    return '{0:{1}} {2}'.format(size/(1024**order), fmt, units[order])


@contextlib.contextmanager
def apply_modules_temporarily(setup='pass', extras=None):
    '''Apply modules temporarily.'''
    if extras is None:
        temp = dict()
    else:
        temp = extras.copy()

    if setup != 'pass':
        code = compile(setup, DUMMY_SRC_NAME, 'exec')
        exec(code, globals(), temp)

    for key in list(temp):
        if key in globals().keys():
            temp.pop(key)

    globals().update(temp)

    try:
        yield
    finally:
        # Restore.
        for key in temp.keys():
            globals().pop(key, None)


class Transformer(ast.NodeTransformer):
    '''Add tracemalloc functions.'''
    def __init__(self, result_id):
        self._result_id = result_id

    def visit_FunctionDef(self, node):
        # Pre-hook.
        pre_hook_expr = ast.Expr(
            value=ast.Call(
                func=ast.Name(id='start', ctx=ast.Load()),
                args=[],
                keywords=[]
            )
        )
        # Post-hook.
        finalbody = [
            ast.Global(names=[self._result_id]),
            ast.Assign(
                targets=[ast.Name(id=self._result_id, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='take_snapshot', ctx=ast.Load()),
                    args=[],
                    keywords=[]
                )
            ),
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id='stop', ctx=ast.Load()),
                    args=[],
                    keywords=[]
                )
            )
        ]

        body_elems = [pre_hook_expr]
        body_elems.extend([elem for elem in node.body])
        node.body.clear()
        node.body.append(
            ast.Try(
                body=body_elems,
                handlers=[],
                orelse=[],
                finalbody=finalbody
            )
        )

        return ast.fix_missing_locations(node)


class CodeBlockCollector(ast.NodeVisitor):
    '''Collect code blocks.'''
    def __init__(self):
        self.code_blocks = dict()

    def visit_FunctionDef(self, node):
        self.code_blocks[node.name] = (node.lineno, node.body[-1].lineno)


class DependencyCollector(ast.NodeVisitor):
    '''Collect dependencies.'''
    def __init__(self):
        self.dependencies = set()

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            self.dependencies.add(node.value.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.dependencies.add(node.func.id)
        self.generic_visit(node)


def extract_dependencies(obj):
    '''Extract dependencies.'''
    source = inspect.getsource(obj)
    source = textwrap.dedent(source)
    node = ast.parse(source)

    collector = DependencyCollector()
    collector.visit(node)

    module = inspect.getmodule(obj)
    actual_dependencies = dict()
    for key in collector.dependencies:
        if key in module.__dict__.keys():
            actual_dependencies[key] = module.__dict__.get(key)

    return actual_dependencies


class Tracer(object):
    '''Tracing malloc that occurs inside a function or method.

    Args:
        function_or_method:
        enable_auto_resolve (bool):
        setup (str): Compile-time dependencies.
            This parameter is ignored if enable_auto_resolve is enabled.
    '''
    def __init__(
        self,
        function_or_method,
        enable_auto_resolve=True,
        setup='pass'
    ):
        if not (inspect.isfunction(function_or_method)
                or inspect.ismethod(function_or_method)):
            raise TypeError('The obj must be a function or a method.')

        if enable_auto_resolve:
            dependencies = extract_dependencies(function_or_method)
            setup = 'pass'
        else:
            dependencies = dict()

        with apply_modules_temporarily(setup=setup, extras=dependencies):
            source_lines, lineno = inspect.getsourcelines(function_or_method)
            source_text = ''.join(source_lines)
            source_text = textwrap.dedent(source_text)
            source_text = source_text.strip()

            node = ast.parse(source_text)
            node = Transformer(result_id='SNAPSHOT').visit(node)

            locals_ = dict()
            code = compile(node, DUMMY_SRC_NAME, 'exec')
            exec(code, globals(), locals_)

        new_obj = locals_[function_or_method.__name__]
        if hasattr(new_obj, '__func__'):
            # class method or static method.
            self._function_or_method = new_obj.__func__
        else:
            # function or method
            self._function_or_method = new_obj

        if hasattr(function_or_method, '__self__'):
            self._class_instance = function_or_method.__self__
        else:
            self._class_instance = None

        self._source_lines = source_lines
        self._lineno = lineno
        self._filepath = inspect.getfile(function_or_method)
        self._enable_auto_resolve = enable_auto_resolve
        self._dependencies = dependencies

    def _take_snapshot(
        self,
        target_args=None,
        setup='pass'
    ):
        '''Take the snapshot.

        Args:
            target_args (dict):
            setup (str): Run-time dependencies.
                This parameter is ignored if enable_auto_resolve is enabled.

        Returns:
            tracemalloc.Snapshot
        '''
        extras = {'SNAPSHOT': None}
        if self._enable_auto_resolve:
            extras.update(self._dependencies)
            setup = 'pass'

        with apply_modules_temporarily(setup=setup, extras=extras):
            global SNAPSHOT

            if target_args is None:
                target_args = dict()

            if self._class_instance is None:
                self._function_or_method(**target_args)
            else:
                self._function_or_method(self._class_instance, **target_args)

            return SNAPSHOT

    def trace(
        self,
        target_args=None,
        setup='pass'
    ):
        '''Display the trace result.

        Args:
            target_args (dict):
            setup (str): Run-time dependencies.
                This parameter is ignored if enable_auto_resolve is enabled.
        '''
        snapshot = self._take_snapshot(
            target_args=target_args,
            setup=setup
        )
        snapshot = snapshot.filter_traces([Filter(True, DUMMY_SRC_NAME), ])
        stats = snapshot.statistics('lineno')

        total = 0
        detected_lines = dict()
        for stat in stats:
            frame = stat.traceback[0]
            detected_lines[str(frame.lineno)] = stat.size
            total += stat.size

        print('File "{}"'.format(self._filepath))
        print('Total {}(raw {} B)'.format(bytes_to_hrf(total), total))
        print('Line #    Trace         Line Contents')
        print('=' * (24+80))

        source_text = ''.join(self._source_lines).rstrip()

        for lineno, line in enumerate(source_text.split(sep='\n'), 1):
            size = detected_lines.get(str(lineno))
            trace = ' ' * 10 if size is None else bytes_to_hrf(size)
            print('{lineno:6d}    {trace:10s}    {contents}'.format(
                lineno=self._lineno + lineno - 1,
                trace=trace,
                contents=line
            ))
