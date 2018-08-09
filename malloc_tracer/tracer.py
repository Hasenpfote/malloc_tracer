#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import ast
import math
import contextlib
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
    # source = textwrap.dedent(source)
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

    def __init__(
        self,
        obj,
        setup='pass',
        enable_auto_resolve=False
    ):
        if not (inspect.isfunction(obj) or inspect.isclass(obj)):
            raise TypeError('The obj must be a function or a class.')

        if enable_auto_resolve:
            dependencies = extract_dependencies(obj)
            setup = 'pass'
        else:
            dependencies = dict()

        with apply_modules_temporarily(setup=setup, extras=dependencies):
            source_lines, lineno = inspect.getsourcelines(obj)
            source_text = ''.join(source_lines).strip()

            node = ast.parse(source_text)

            collector = CodeBlockCollector()
            collector.visit(node)

            node = Transformer(result_id='SNAPSHOT').visit(node)

            locals_ = {}
            code = compile(node, DUMMY_SRC_NAME, 'exec')
            exec(code, globals(), locals_)

        self._obj = locals_[obj.__name__]
        self._source_lines = source_lines
        self._lineno = lineno
        self._filepath = inspect.getfile(obj)
        self._code_blocks = collector.code_blocks
        self._enable_auto_resolve = enable_auto_resolve
        self._dependencies = dependencies

    def _take_snapshot(
        self,
        init_args=None,
        target_name=None,
        target_args=None,
        setup='pass'
    ):
        extras = {'SNAPSHOT': None}
        if self._enable_auto_resolve:
            extras.update(self._dependencies)
            setup = 'pass'

        with apply_modules_temporarily(setup=setup, extras=extras):
            global SNAPSHOT

            if target_args is None:
                target_args = dict()

            if inspect.isfunction(self._obj):
                self._obj(**target_args)
            else:
                if isinstance(self._obj.__dict__[target_name], staticmethod) \
                        or isinstance(self._obj.__dict__[target_name], classmethod):
                    method = getattr(self._obj, target_name)
                else:
                    if init_args is None:
                        init_args = dict()

                    instance = self._obj(**init_args)
                    method = getattr(instance, target_name)

                method(**target_args)

            return SNAPSHOT

    def trace(
        self,
        init_args=None,
        target_name=None,
        target_args=None,
        setup='pass',
        verbose=False
    ):
        if inspect.isfunction(self._obj):
            target_name = self._obj.__name__

        snapshot = self._take_snapshot(
            init_args=init_args,
            target_name=target_name,
            target_args=target_args,
            setup=setup
        )
        snapshot = snapshot.filter_traces([Filter(True, DUMMY_SRC_NAME), ])
        stats = snapshot.statistics('lineno')

        total = 0
        detected_lines = {}
        for stat in stats:
            frame = stat.traceback[0]
            detected_lines[str(frame.lineno)] = stat.size
            total += stat.size

        print('File "{}"'.format(self._filepath))
        prefix = '' if inspect.isfunction(self._obj) else self._obj.__name__ + '.'
        print('Target', prefix + target_name)
        print('Total {}(raw {} B)'.format(bytes_to_hrf(total), total))
        print('Line #    Trace         * Line Contents')
        print('=' * (26+80))

        code_block = self._code_blocks.get(target_name)
        source_text = ''.join(self._source_lines).strip()

        for lineno, line in enumerate(source_text.split(sep='\n'), 1):
            if verbose:
                marker = '*' if code_block[0] <= lineno <= code_block[1] else ' '
            else:
                if (lineno < code_block[0]) or (lineno > code_block[1]):
                    continue
                marker = ' '

            size = detected_lines.get(str(lineno))
            trace = ' ' * 10 if size is None else bytes_to_hrf(size)
            print('{lineno:6d}    {trace:10s}    {marker} {contents}'.format(
                lineno=self._lineno + lineno - 1,
                trace=trace,
                marker=marker,
                contents=line
            ))
