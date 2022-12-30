# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib.machinery
import os
import sys

import adbutils
import uiautomator2

import droidctl.app
import droidctl.fdroid
import droidctl.settings
import droidctl.util


class Device:
    name = None  # can be set to pretty name in preamble, defaults to adb id
    # all useful things are namespaced under the following attributes:
    adb = None  # adbutils functionality
    ui = None  # uiautomator2 functionality
    fdroid = None  # fdroid functionality, backed by fdroidcl
    settings = None  # settings functionality, backed by adb commands

    def __init__(self, id_=None):
        # List devices through adb
        adb = adbutils.AdbClient()
        devices = adb.device_list()
        # Ensure there's just one
        assert len(devices) > 0, 'No devices found!'
        assert len(devices) == 1, 'More than one device found!'
        # Attach adb functionality under .adb
        self.adb = devices[0]
        id_c = self.adb.serial
        # Ensure it's the right one
        if id_:
            assert id_c == id_, f'Wrong device {id_c} is not {id_}!'
        self.name = id_c

        # Attach uiautomator2 functionality under .ui
        self.ui = uiautomator2.connect(id_c)

        # Attach fdroidcl functionality under .fdroid
        self.fdroid = droidctl.fdroid.FDroidCL(self, id_c)

        # Attach adb settings functionality under .settings
        self.settings = droidctl.settings.Settings(self)

    def __call__(self, cmd, **kwa):
        r = self.adb.shell2(cmd, **kwa)
        if r.returncode:
            print(f'Execution of `{cmd}` has failed with {r.returncode}:')
            print(r.output)
            sys.exit(1)
        return r

    def app(self, *a, **kwa):
        return droidctl.app.App(self, *a, **kwa)

    def apply(self, path, *args, _func='run', **kwargs):
        return droidctl.util.apply(self, path, *args, _func=_func, **kwargs)
