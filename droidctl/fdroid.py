# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess

import droidctl.app


class FDroidCL:
    def __init__(self, d, id_):
        # TODO: somehow ensure it's the right device ID
        # only thing fdroidcl ensures is the amount of devices
        self.id_ = id_
        self._d = d

    def install(self, *appids):
        subprocess.run(['fdroidcl', 'install', *appids], check=True)

    def uninstall(self, *appids):
        subprocess.run(['fdroidcl', 'uninstall', *appids], check=True)

    def __getitem__(self, name):
        return droidctl.app.App(self._d, name, store=self)
