import numpy as np
from repay.sim import run
from repay.mechanisms import Repay, PlainDPP
from repay.params import Params
from experiments.common import pmap, MECHS
from experiments.data_real import make_real_trace
def job(j):
    mech,qsmode,k=j
    tr,meta=make_real_trace('PW0127',k,7200,load=1.0,classes='log',tiers='estimated')
    qs=1.0 if qsmode=='orig' else 1.0/float(np.mean(tr['C']))
    p=Params(queue_scale=qs)
    r=run(tr,MECHS[mech](p),p)
    return dict(mech=mech,qs=qsmode,k=k,rt=r['rt_success']['all'],el=r['el_rate'],env=r['max_env'],P=r['served_ratio']['P'],Y=r['served_ratio'].get('Y'),F=r['free_floor_ratio'])
jobs=[(m,q,k) for m in ['repay','no-debt','dpp'] for q in ['orig','norm'] for k in range(6)]
res=pmap(job,jobs,procs=4)
for m in ['repay','no-debt','dpp']:
  for q in ['orig','norm']:
    rs=[r for r in res if r['mech']==m and r['qs']==q]
    f=lambda k: np.nanmean([np.nan if r[k] is None else r[k] for r in rs])
    print(f"{m:8s} {q:5s} RT={100*f('rt'):5.1f} el={f('el'):.3f} env={f('env'):7.1f} P={f('P'):.3f} Y={f('Y'):.3f} F={f('F'):.3f} Pmin={min(r['P'] for r in rs):.3f}")
