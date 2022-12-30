# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later


class App:
    def __init__(self, d, id_, store=None, autoinstall=True):
        # TODO: somehow ensure it's the right device ID
        # only thing fdroidcl ensures is the amount of devices
        self._d = d
        self.id_ = id_
        self.store = store

        if store is not None and autoinstall:
            self.install()

    def is_installed(self):
        # TODO: something faster?
        return self.id_ in self._d.adb.list_packages()

    def install(self):
        if self.store is not None:
            if not self.is_installed():
                self.store.install(self.id_)
        else:
            raise NotImplementedError('store not specified,'
                                      f' cannot install {self.id_}')
        assert self.is_installed()

    def uninstall(self):
        if self.store is not None:
            self.store.uninstall(self.id_)
        else:
            self._d.adb.uninstall(self.id_)
        assert not self.is_installed()

    def allow_notifications(self):
        self._d(f'pm set-permission-flags {self.id_}'
                ' android.permission.POST_NOTIFICATIONS user-set')

    def grant(self, *perms):
        for perm in perms:
            self._d(f'pm grant {self.id_} {perm}')
