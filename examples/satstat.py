import xml.etree.ElementTree as ET


def run(d):
    satstat = d.fdroid['com.vonglasow.michael.satstat']
    satstat.permissions.allow_notifications()
    satstat.permissions += 'android.permission.ACCESS_COARSE_LOCATION'
    satstat.permissions += 'android.permission.ACCESS_FINE_LOCATION'
    satstat.permissions += 'android.permission.ACCESS_BACKGROUND_LOCATION'

    satstat.launch()
    d.ui.press('menu')
    print('settings')
    d.ui(text='Settings').click()
    print('menu')
    d.ui.press('back')

    # Now we have the settings file generated and we can edit it
    with satstat.shared_prefs[f'{satstat.id_}_preferences'] as p:
        # Auto-update on all networks, example of low-level XML work
        un = p.xml.findall("./set[@name='pref_update_networks']")[0]
        while len(un):
            un.remove(un[0])
        for i in 0, 1, 7, 9, 10, 11, 12, 13, 14, 15, 17:
            ET.SubElement(un, 'string').text = str(i)
        # Example of higher-level API
        assert 'pref_unit_type' in p
        p['pref_unit_type'] = False
        assert p['pref_unit_type'] is False
        p['pref_unit_type'] = True
        assert p['pref_unit_type'] is True

    satstat.launch()
    d.ui.press('menu')
    d.ui(text='Reload AGPS data').click()
    d.ui.press('home')
