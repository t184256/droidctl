# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess

import droidctl.app


class FDroidCL:
    def __init__(self, d, id_):
        self.id_ = id_
        self._d = d
        self.serial = self._d.adb.serial

    def install(self, *appids):
        subprocess.run(['fdroidcl', 'install', *appids], check=True,
                       env={**os.environ, 'ANDROID_SERIAL': self.serial})

    def uninstall(self, *appids):
        subprocess.run(['fdroidcl', 'uninstall', *appids], check=True,
                       env={**os.environ, 'ANDROID_SERIAL': self.serial})

    def __getitem__(self, name):
        return droidctl.app.App(self._d, name, store=self)
