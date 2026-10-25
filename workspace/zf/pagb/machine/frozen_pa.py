"""Read-only access to the FROZEN pagb machine (design A(a), 449 states; freeze record in ../INTERFACE.md).

The frozen files are read-only and must not be rebuilt in place. Tools call `machine_path(suffix)`:
the frozen machine (suffix '') is only read and hash-checked; other variants (e.g. the positive control
'_ctl') are built by design.build_files() into their own, writable files.
"""
import os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))

FROZEN = {
    'pa_wade.tm': 'ed795af79b6752d72c037d7e32eca1d23efaa6a6c0f0d07fc7ba89869f2616a6',
    'source_pa.py': '152d4a5f82be2f12c3823478a911c5f71fd21f78a21bca06f690030582b42587',
    'spec_pa.py': '3cfdafbfe00828621ffdcddac7de09c57418a3b8eeadc08d2ee681ab9828dde4',
    'design_choice_A.json': 'da10ced32774ea0ea3ea91f1d84d3fe15ef17324e760579165586b431fd7abf9',
}

def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()

def check_frozen(names=None):
    """assert that the frozen files on disk have the recorded hashes."""
    for n in (names or FROZEN):
        h = sha(os.path.join(HERE, n))
        assert h == FROZEN[n], f'{n}: sha256 {h} differs from the frozen {FROZEN[n]}'
    return True

def machine_path(suffix=''):
    """path of the compiled .tm for a design variant; never rebuilds the frozen one."""
    path = os.path.join(HERE, f'pa{suffix}_wade.tm')
    if suffix == '':
        check_frozen(['pa_wade.tm', 'source_pa.py'])
        return path
    import design
    design.build_files()
    return path

if __name__ == '__main__':
    check_frozen()
    print('frozen files OK:', ', '.join(FROZEN))
