def run(d):
    d.adb.shell('am start -a android.settings.SETTINGS')
    d.ui.press('home')
