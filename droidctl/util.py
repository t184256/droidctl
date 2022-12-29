# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
droidctl: a helper to control Android devices with scripts
Allows writing concise scripts that do something with Android devices:
install apps, click through menus to configure settings, etc.
"""

import importlib.machinery
import os


def _print_header(s, **kwa):
    l = len(s)
    print('- ' + s + ((' ' + '-' * (80 - 3 - l)) if l < 80 - 3 else ''), **kwa)


def apply(d, path, *args, root='.', _func='run', **kwargs):
    name, _ = os.path.splitext(os.path.basename(os.path.join(root, path)))
    module = importlib.machinery.SourceFileLoader(name, path).load_module()
    assert _func in dir(module), f'module {name} lacks {_func}(d)!'

    nice_args = ', '.join(
        [repr(arg) for arg in args] +
        [f'{k}={repr(v)}' for k, v in kwargs.items()]
    )
    _print_header(f'Executing {name}.{_func}({nice_args}) against {d.name}')

    return getattr(module, _func)(d) or d
