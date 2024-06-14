def run(d):
    d.fdroid.install('com.simplemobiletools.thankyou',
                     'com.uberspot.a2048')
    pkgs = d.adb.list_packages()
    assert 'com.simplemobiletools.thankyou' in pkgs
    assert 'com.uberspot.a2048' in pkgs

    d.fdroid.uninstall('com.simplemobiletools.thankyou',
                       'com.uberspot.a2048')
    pkgs = d.adb.list_packages()
    assert 'com.simplemobiletools.thankyou' not in pkgs
    assert 'com.uberspot.a2048' not in pkgs

    # Or, much terser and with rich App objects
    d.fdroid['com.simplemobiletools.thankyou'].uninstall()
