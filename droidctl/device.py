# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

import ppadb.client
import uiautomator

import droidctl.fdroid
import droidctl.settings


class Device:
    name = None  # can be set to pretty name in preamble, defaults to adb id
    # all useful things are namespaced under the following attributes:
    adb = None  # adb functionality
    ui = None  # uiautomator functionality
    fdroid = None  # fdroid functionality, backed by fdroidcl
    settings = None  # settings functionality, backed by adb commands

    def __init__(self, id_=None):
        # List devices through adb
        adb = ppadb.client.Client()
        devices = adb.devices()
        # Ensure there's just one
        assert len(devices) > 0, 'No devices found!'
        assert len(devices) == 1, 'More than one device found!'
        # Attach adb functionality under .adb
        self.adb = devices[0]
        id_c = self.adb.get_serial_no()
        # Ensure it's the right one
        if id_:
            assert id_c == id_, f'Wrong device {id_c} is not {id_}!'
        self.name = id_c

        # Attach uiautomator functionality under .ui
        self.ui = uiautomator.Device(id_c)

        # Attach fdroidcl functionality under .fdroid
        self.fdroid = droidctl.fdroid.FDroidCL(id_c)

        # Attach adb settings functionality under .settings
        self.settings = droidctl.settings.Settings(self)

    def __call__(self, cmd, **kwa):
        r = self.adb.shell(f'({cmd}) && echo - success', **kwa)
        if not r.endswith('- success\n'):
            print(f'Execution of command {cmd} has failed:')
            print(r)
            sys.exit(1)
        return r.removesuffix('- success\n')
