# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

class Settings:
    def __init__(self, d):
        self._d = d

    def __getitem__(self, namespace):
        return SettingsProxy(self._d, namespace)


class SettingsProxy:
    def __init__(self, d, namespace):
        self.__d = d
        self.__ns = namespace

    def __getitem__(self, name):
        v = self.__d(f'settings get "{self.__ns}" "{name}"').removesuffix('\n')
        return v

    def __setitem__(self, name, val):
        self.__d(f'settings put "{self.__ns}" "{name}" "{val}"')
        assert self[name] == str(val)

    def __contains__(self, name):
        # TODO: faster way?
        r = '\n' + self.__d(f'settings list "{self.__ns}"')
        return f'\n{name}=' in r
