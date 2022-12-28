def preamble(d):
    d.meta = object()
    if d.adb.get_serial_no() == 'R3CN90YJFEM':
        d.name = 'carambola'
    return d
