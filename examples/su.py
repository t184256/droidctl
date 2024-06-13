def run(d):
    print('/bin/echo x')
    r = d('/bin/echo x')
    assert r.returncode == 0
    assert r.output == 'x\n', repr(r.output)

    print(['/bin/echo', 'x'])
    r = d(['/bin/echo', 'x'])
    assert r.returncode == 0
    assert r.output == 'x\n', repr(r.output)

    print('su + /bin/echo x')
    r = d.su('/bin/echo x')
    assert r.returncode == 0
    # IDK why 'su 0' CRLFs
    assert r.output.replace('\r\n', '\n') == 'x\n', repr(r.output)

    print('su + /bin/echo x < /dev/null')
    r = d.su('/bin/echo x < /dev/null')
    assert r.returncode == 0
    # IDK why 'su 0' CRLFs
    assert r.output.replace('\r\n', '\n') == 'x\n', repr(r.output)

    print('su + id')
    r = d.su('id')
    assert r.returncode == 0
    assert r.output.startswith('uid=0(root) gid=0(root)'), repr(r.output)
