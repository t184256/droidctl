# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib
import os
import sqlite3
import tempfile
import time
import xml.etree.ElementTree as ET


class App:
    def __init__(self, d, id_, store=None, url=None, autoinstall=True):
        # TODO: somehow ensure it's the right device ID
        # only thing fdroidcl ensures is the amount of devices
        self._d = d
        self.id_ = id_
        self.store = store
        self.url = url
        self.shared_prefs = SharedPrefs(d, id_)
        self.sqlite = SQLite(d, id_)
        self.permissions = Permissions(d, id_)

        if autoinstall and (store or url):
            self.install()

    def is_installed(self):
        # TODO: something faster?
        return self.id_ in self._d.adb.list_packages()

    def install(self):
        if self.is_installed():
            return

        if self.store is not None:
            if not self.is_installed():
                self.store.install(self.id_)
        elif self.url is not None:
            self._d.adb.install(self.url)
        else:
            raise NotImplementedError('neither store nor url are specified,'
                                      f' cannot install {self.id_}')
        assert self.is_installed()

    def uninstall(self):
        if self.store is not None:
            self.store.uninstall(self.id_)
        else:
            self._d.adb.uninstall(self.id_)
        assert not self.is_installed()

    def clear(self):
        self._d(f'pm clear {self.id_}')

    def stop(self):
        self._d(f'am stop-app {self.id_}')

    def launch(self, wait=True):
        self._d.ui.app_start(self.id_)
        if wait:
            self.wait()

    def wait(self):
        while self._d.ui.info['currentPackageName'] != self.id_:
            time.sleep(.25)


class SharedPrefs:
    def __init__(self, d, id_):
        self._d = d
        self._id = id_

    @contextlib.contextmanager
    def xml(self, fname):
        self._d(f'am stop-app {self._id}')
        path = f'/data/data/{self._id}/shared_prefs/{fname}'
        t = self._d(f'su -c "cat {path}"').output
        xml = ET.fromstring(t)
        yield xml
        xml = ET.tostring(xml, encoding='utf8', method='xml')
        tmp_path = f'/data/local/tmp/{fname}'
        self._d.adb.sync.push(xml, tmp_path)
        self._d(f'su -c "cat {tmp_path} > {path}"')
        self._d(f'rm {tmp_path}')


class SQLite:
    def __init__(self, d, id_):
        self._d = d
        self._id = id_

    @contextlib.contextmanager
    def db(self, fname):
        self._d(f'am stop-app {self._id}')
        path = f'/data/data/{self._id}/databases/{fname}'
        tmp_path = f'/data/local/tmp/{fname}'
        self._d(f'su -c "cat {path}" > {tmp_path}')
        with tempfile.TemporaryDirectory() as td:
            tf = os.path.join(td, fname)
            self._d.adb.sync.pull(tmp_path, tf)
            with sqlite3.connect(tf) as con:
                yield con
            self._d.adb.sync.push(tf, tmp_path)
        self._d(f'su -c "cat {tmp_path} > {path}"')
        self._d(f'rm {tmp_path}')


class Permissions:
    def __init__(self, d, id_):
        self._d = d
        self._id = id_

    def allow_notifications(self):
        self._d(f'pm set-permission-flags {self._id}'
                ' android.permission.POST_NOTIFICATIONS user-set')

    def disallow_notifications(self):
        self -= 'android.permission.POST_NOTIFICATIONS'
        self._d(f'pm set-permission-flags {self._id}'
                ' android.permission.POST_NOTIFICATIONS user-set')

    def allow_unrestricted_battery(self):
        self._d(f'dumpsys deviceidle whitelist +{self._id}')

    def grant(self, *perms):
        for perm in perms:
            self += perm

    def __iadd__(self, perm):
        self._d(f'pm grant {self._id} {perm}')
        return self

    def revoke(self, *perms):
        for perm in perms:
            self -= perm

    def __isub__(self, perm):
        self._d(f'pm revoke {self._id} {perm}')
        return self
