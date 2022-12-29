# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
droidctl: a helper to control Android devices with scripts
Allows writing concise scripts that do something with Android devices:
install apps, click through menus to configure settings, etc.
"""

import os
import sys

import click

import droidctl.device


DEFAULT_PREAMBLE_PATH = 'preamble.py'


@click.group(help=__doc__)
def cli():
    pass


@cli.command()
@click.argument('script', nargs=-1, required=True,
                type=click.Path(readable=True))
@click.option('--root', type=click.Path(readable=True),
              help='path to resolving imports in scripts')
@click.option('--preamble', type=click.Path(readable=True),
              help='preamble script')
@click.option('--device', type=click.STRING, help='ADB device id')
def run(script, preamble, device, root):
    # simplify importing for scripts
    bak_path = sys.path
    root = root or os.getcwd()
    sys.path.append(root)

    d = droidctl.device.Device(device)

    # Load preamble
    if preamble:
        d = d.apply(preamble, _func='preamble')
    for s in script:
        d = d.apply(s, _func='run')

    sys.path.remove(root)
    assert sys.path == bak_path
    return d
