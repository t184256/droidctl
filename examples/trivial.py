def run(d):
    print(f'Running against device {d.name}')
    print('Google Play is installed:',
          'com.android.vending' in d.adb.list_packages())
    print('Orientation:', d.ui.orientation)
    assert d('echo test') == 'test\n'
