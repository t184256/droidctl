def run(d):
    d.fdroid.install('com.simplemobiletools.thankyou',
                     'de.onyxbits.sensorreadout')
    pkgs = d.adb.list_packages()
    assert 'com.simplemobiletools.thankyou' in pkgs
    assert 'de.onyxbits.sensorreadout' in pkgs

    d.fdroid.uninstall('com.simplemobiletools.thankyou',
                       'de.onyxbits.sensorreadout')
    pkgs = d.adb.list_packages()
    assert 'com.simplemobiletools.thankyou' not in pkgs
    assert 'de.onyxbits.sensorreadout' not in pkgs

    # Or, much terser and with rich App objects
    d.fdroid['com.simplemobiletools.thankyou'].uninstall()
