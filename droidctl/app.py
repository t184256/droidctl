# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib
import os
import re
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
            self._d.adb.install(self.url, nolaunch=True)
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

    @property
    def uid(self):
        dump = self._d(f'dumpsys package {self.id_}').output
        assert 'userId=' in dump
        return int(re.findall(r'userId=(\d+)', dump)[0])

    def clear(self):
        self._d(f'pm clear {self.id_}')

    def stop(self):
        if self._d.android_version > 12:
            self._d(f'am stop-app {self.id_}')
        else:
            self._d(f'am force-stop {self.id_}')

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

    def __getitem__(self, xmlname):
        return SharedPrefsFile(self._d, self._id, xmlname)


class SharedPrefsFile:
    def __init__(self, d, id_, xmlname):
        self._d = d
        self._id = id_
        self._xmlname = xmlname
        self._path = f'/data/data/{self._id}/shared_prefs/{self._xmlname}.xml'

    def __enter__(self):
        self._d.app(self._id).stop()
        t = self._d(f'su -c "cat {self._path}"').output
        self.xml = ET.fromstring(t)
        return self

    def __exit__(self, *_):
        tmp_path = f'/data/local/tmp/{self._xmlname}.xml'
        s = ET.tostring(self.xml, encoding='utf8', method='xml')
        self._d.adb.sync.push(s, tmp_path)
        self._d(f'su -c "cat {tmp_path} > {self._path}"')
        self._d(f'rm {tmp_path}')
        del self.xml

    def __contains__(self, name):
        return bool(self.xml.findall(f"./*[@name='{name}']"))

    def __getitem__(self, name):
        f = self.xml.findall(f"./*[@name='{name}']")
        if f:
            f = f[0]
            if f.tag == 'string':
                return f.text
            elif f.tag == 'long':
                return int(f.attrib['value'])
            elif f.tag == 'float':
                return float(f.attrib['value'])
            elif f.tag == 'boolean':
                return f.attrib['value'] == 'true'
            else:
                raise NotImplementedError(f'yet unsupported type {f.tag}')

    def __setitem__(self, name, val):
        f = self.xml.findall(f"./*[@name='{name}']")
        if f:
            f = f[0]
            if f.tag == 'string':
                f.text = val
            elif f.tag in ('long', 'float'):
                f.attrib['value'] = str(val)
            elif f.tag == 'boolean':
                f.attrib['value'] = 'true' if val else 'false'
            else:
                raise NotImplementedError(f'yet unsupported type {f.tag}')
        else:
            if isinstance(val, str):
                n = ET.SubElement(self.xml, 'string')
                n.text = val
            elif isinstance(val, bool):
                n = ET.SubElement(self.xml, 'boolean')
                n.attrib['value'] = str(val)
            elif isinstance(val, int):
                n = ET.SubElement(self.xml, 'long')
                n.attrib['value'] = str(val)
            elif isinstance(val, float):
                n = ET.SubElement(self.xml, 'float')
                n.attrib['value'] = str(val)
            elif isinstance(val, tuple) and len(val) == 2:  # custom type
                n = ET.SubElement(self.xml, val[0])
                n.attrib['value'] = str(val[1])
            else:
                raise NotImplementedError(f'yet unsupported type {type(val)}')
            n.attrib['name'] = name


class SQLite:
    def __init__(self, d, id_):
        self._d = d
        self._id = id_

    @contextlib.contextmanager
    def db(self, fname):
        self._d.app(self._id).stop()
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
        self._d(f'pm grant {self._id} android.permission.POST_NOTIFICATIONS',
                check=False)
        if self._d.android_version > 12:
            self._d(f'pm set-permission-flags {self._id}'
                    ' android.permission.POST_NOTIFICATIONS user-set')

    def disallow_notifications(self):
        self._d(f'pm revoke {self._id} android.permission.POST_NOTIFICATIONS',
                check=False)
        if self._d.android_version > 12:
            self._d(f'pm set-permission-flags {self._id}'
                    ' android.permission.POST_NOTIFICATIONS user-set')

    def allow_background(self):
        self._d(f'cmd appops set {self._id} RUN_IN_BACKGROUND allow')
        # adb shell am make-uid-idle ?

    def disallow_background(self):
        self._d(f'cmd appops set {self._id} RUN_IN_BACKGROUND ignore')

    def allow_unrestricted_battery(self):
        self._d(f'dumpsys deviceidle whitelist +{self._id}')

    def grant(self, *perms):
        for perm in perms:
            self += perm

    def __iadd__(self, perm):
        r = self._d.adb.shell2(f'pm grant {self._id} {perm}')
        if 'is not a changeable permission type' in r.output:
            perm = perm.removeprefix('android.permission.')
            self._d(f'appops set {self._id} {perm} allow')
        return self

    def revoke(self, *perms):
        for perm in perms:
            self -= perm

    def __isub__(self, perm):
        r = self._d.adb.shell2(f'pm revoke {self._id} {perm}')
        if 'is not a changeable permission type' in r.output:
            perm = perm.removeprefix('android.permission.')
            self._d(f'appops set {self._id} {perm} ignore')
        return self
