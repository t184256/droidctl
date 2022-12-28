# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

import ppadb.client
import uiautomator

import droidctl.fdroid


class Device:
    name = None  # can be set to pretty name in preamble, defaults to adb id
    # all useful things are namespaced under the following attributes:
    adb = None  # adb functionality
    ui = None  # uiautomator functionality
    fdroid = None  # fdroid functionality

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
