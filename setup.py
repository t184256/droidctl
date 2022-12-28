# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup

setup(
    name='droidctl',
    version='0.0.1',
    url='https://github.com/t184256/droidctl',
    author='Alexander Sosedkin',
    author_email='monk@unboiled.info',
    description="a helper to control Android devices with scripts",
    packages=[
        'droidctl',
    ],
    install_requires=[
        'uiautomator',
        'pure-python-adb',
    ],
    entry_points={
        'console_scripts': [
            'droidctl = droidctl.app:cli',
        ],
    },
)
