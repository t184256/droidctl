# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

class Settings:
    def __init__(self, d):
        self._d = d

    def __setattr__(self, name, val):
        self._d(f'settings put global "{name}" "{val}"')
        assert self._d(f'settings get global "{name}"') == str(val)

    def __getattr__(self, name):
        return self._d(f'settings get global "{name}"')
