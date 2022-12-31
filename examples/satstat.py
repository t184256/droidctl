import xml.etree.ElementTree as ET


def run(d):
    satstat = d.fdroid['com.vonglasow.michael.satstat']
    satstat.allow_notifications()
    satstat.grant(
        'android.permission.ACCESS_COARSE_LOCATION',
        'android.permission.ACCESS_FINE_LOCATION',
        'android.permission.ACCESS_BACKGROUND_LOCATION',
    )

    satstat.launch()
    d.ui.press('menu')
    print('settings')
    d.ui(text='Settings').click()
    print('menu')
    d.ui.press('back')

    # Now we have the settings file generated and we can edit it
    with satstat.shared_prefs.xml(f'{satstat.id_}_preferences.xml') as xml:
        # Auto-update on all networks
        un = xml.findall("./set[@name='pref_update_networks']")[0]
        while len(un):
            un.remove(un[0])
        for i in 0, 1, 7, 9, 10, 11, 12, 13, 14, 15, 17:
            ET.SubElement(un, 'string').text = str(i)
        ET.dump(un)
        print('---')
        ET.dump(xml)

    satstat.launch()
    d.ui.press('menu')
    d.ui(text='Reload AGPS data').click()
    d.ui.press('home')
