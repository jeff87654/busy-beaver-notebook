"""Build the m254gb machine from the chosen NG' (chosen.json: module, builder, options, labels).

    python ng_final.py            writes source_gb.py and m254gb_wade.tm, prints states, tokens,
                                  the named and the labelled reading of NG'
    python ng_final.py control    positive control: NG' replaced by  ∃v1 v1∈v1  (source_gbctl.py)
"""
import sys, os, json, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ngdsl

def chosen():
    c = json.load(open(os.path.join(HERE, 'chosen.json'), encoding='utf-8'))
    mod = importlib.import_module(c['module'])
    o = dict(mod.DEFAULT); o.update(c['o'])
    f = getattr(mod, c['builder'])(o)
    lab = c['lab']
    assert ngdsl.check(f, lab), 'chosen labelling captures a variable'
    return f, lab, c

def ng_tokens():
    f, lab, c = chosen()
    return ngdsl.rpn(f, lab)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'control':
        ctl = ngdsl.ex('x', ngdsl.el('x', 'x'))
        toks = ngdsl.rpn(ctl, {'x': 1})
        st = ngdsl.compile_tokens(ngdsl.bundle_tokens(toks), 'gbctl', save='m254gb_control.tm')
        print('control (NG := E.v1 v1 e. v1): tokens', len(toks), 'states', st)
        sys.exit()
    f, lab, c = chosen()
    toks = ngdsl.rpn(f, lab)
    st = ngdsl.compile_tokens(ngdsl.bundle_tokens(toks, c.get('place', 'after')), 'gb', save='m254gb_wade.tm')
    print('NG tokens', len(toks), ' bundle tokens', len(ngdsl.bundle_tokens(toks)), ' states', st, f'(baseline 281, +{st - 281})')
    print('labels used', sorted(set(lab.values())))
    print('named   :', ngdsl.show(f))
    print('labelled:', ngdsl.show(f, lab))
