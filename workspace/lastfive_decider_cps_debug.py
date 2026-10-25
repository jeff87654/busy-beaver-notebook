import faulthandler,json
from lastfive_decider_cps import child
faulthandler.dump_traceback_later(5,repeat=True)
p={'id':'cal_runaway','machine':'1RA1RA','setting':0,'history':2,'block':1,'window':3,'max_steps':100000,'max_configs':10000,'max_edges':10000,'timeout':10}
print(json.dumps(child(p)),flush=True)
faulthandler.cancel_dump_traceback_later()
