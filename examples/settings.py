def run(d):
    assert 'nonex' not in d.settings['global']
    assert 'animator_duration_scale' in d.settings['global']
    old = d.settings['global']['animator_duration_scale']
    d.settings['global']['animator_duration_scale'] = '2.00'
    assert d.settings['global']['animator_duration_scale'] == '2.00'
    d.settings['global']['animator_duration_scale'] = old
    assert d.settings['global']['animator_duration_scale'] == old
