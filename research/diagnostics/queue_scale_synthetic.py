import numpy as np, sys
from repay.sim import make_trace, run, HOTSPOT_DEFAULTS as H
from repay.mechanisms import Repay
from repay.params import Params
from experiments.common import pmap
BIND=dict(w=(1.0,1.0,1.0), commit=(float("inf"),3.0,2.0), theta_P=0.8, theta_Y=0.7, phi=0.2)
def job(j):
    cfg,qs,seed=j
    s=4.0 if cfg=='scale4' else 1.0
    tr=make_trace('hotspot',6000,seed,arr_rate=H['arr_rate']*s,burst_size=H['burst_size']*s,C_mean=H['C_mean']*s)
    kw=dict(BIND) if cfg=='binding' else {}
    p=Params(queue_scale=qs,**kw)
    r=run(tr,Repay(p),p)
    return dict(cfg=cfg,qs=qs,seed=seed,rt=r['rt_success']['all'],el=r['el_rate'],env=r['max_env'],P=r['served_ratio']['P'],Y=r['served_ratio']['Y'],F=r['free_floor_ratio'],db=r.get('D_over_B_max'))
jobs=[(c,q,s) for c in ['default','binding','scale4'] for q in [1.0,0.1,0.01] for s in [0,1]]
res=pmap(job,jobs,procs=4)
for c in ['default','binding','scale4']:
  for q in [1.0,0.1,0.01]:
    rs=[r for r in res if r['cfg']==c and r['qs']==q]
    m=lambda k: np.mean([r[k] for r in rs])
    print(f"{c:8s} qs={q:5} RT={100*m('rt'):5.1f} el={m('el'):.3f} env={m('env'):6.1f} P={m('P'):.3f} Y={m('Y'):.3f} F={m('F'):.3f} DB={m('db'):.3f}")
