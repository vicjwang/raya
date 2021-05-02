
def convert_dms_to_dd(d, m, s, ref):
    dd = d + m / 60 + s / 3600
    if ref in ('S', 'W'):
        dd = -dd
    return dd

