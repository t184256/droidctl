def preamble(d):
    d.meta = object()
    if d.adb.serial == 'R3CN90YJFEM':
        d.name = 'carambola'
    return d
