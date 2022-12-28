# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
droidctl: a helper to control Android devices with scripts
Allows writing concise scripts that do something with Android devices:
install apps, click through menus to configure settings, etc.
"""

import importlib.machinery
import os

import click

import droidctl.device


DEFAULT_PREAMBLE_PATH = 'preamble.py'


@click.group(help=__doc__)
def cli():
    pass


def _print_header(s, **kwa):
    l = len(s)
    print('- ' + s + ((' ' + '-' * (80 - 3 - l)) if l < 80 - 3 else ''), **kwa)


@cli.command()
@click.argument('script', nargs=-1, required=True,
                type=click.Path(readable=True))
@click.option('--preamble', type=click.Path(readable=True),
              help='preamble script')
@click.option('--device', type=click.STRING, help='ADB device id')
def run(script, preamble, device):
    d = droidctl.device.Device(device)

    # Load preamble
    if preamble:
        p = importlib.machinery.SourceFileLoader(
            'preamble', preamble
        ).load_module()
        assert 'preamble' in dir(p), f'Preamble file {p} lacks preamble(d)!'
        _print_header(f'Executing preamble {preamble} against {d.name}')
        assert 'preamble' in dir(p), f'preamble {p} lacks prealmble(d)!'
        d = p.preamble(d) or d
    for s in script:
        s_name, _ = os.path.splitext(os.path.basename(s))
        module = importlib.machinery.SourceFileLoader(s_name, s).load_module()
        assert 'run' in dir(module), f'module {s_name} lacks run(d)!'
        _print_header(f'Executing {s_name} against {d.name}')
        d = module.run(d) or d
