import faulthandler
faulthandler.dump_traceback_later(5,repeat=False,exit=True)
print('before import',flush=True)
from lastfive_decider_cps import child
print('after import',flush=True)
p={'id':'cal_runaway','machine':'1RA1RA','setting':0,'history':2,'block':1,'window':3,'max_steps':100000,'max_configs':10000,'max_edges':10000,'timeout':10}
print(child(p),flush=True)
faulthandler.cancel_dump_traceback_later()
