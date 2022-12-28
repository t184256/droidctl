def run(d):
    d.fdroid.install('com.simplemobiletools.thankyou',
                     'de.onyxbits.sensorreadout')
    assert d.adb.is_installed('com.simplemobiletools.thankyou')
    assert d.adb.is_installed('de.onyxbits.sensorreadout')
    d.fdroid.uninstall('com.simplemobiletools.thankyou',
                       'de.onyxbits.sensorreadout')
    assert not d.adb.is_installed('com.simplemobiletools.thankyou')
    assert not d.adb.is_installed('de.onyxbits.sensorreadout')
