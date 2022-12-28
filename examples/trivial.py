def run(d):
    print(f'Running against device {d.name}')
    print('Google Play is installed:',
          d.adb.is_installed('com.android.vending'))
    print('Orientation:', d.ui.orientation)
    assert d.adb.is_installed('com.github.uiautomator')  # gets autoinstalled
