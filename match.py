import pandas
import statsmodels.api
from numpy import *
from expiringdict import ExpiringDict

data1 = None
data2 = None
senders = ExpiringDict(max_len=100, max_age_seconds=10)
receivers = ExpiringDict(max_len=100, max_age_seconds=10)
result = ExpiringDict(max_len=100, max_age_seconds=3600)

def corr(y1, y2):
    return corrcoef(y1, y2, 0)[0][1]

def granger(y1, y2, l = 20):
    model = statsmodels.tsa.vector_ar.var_model.VAR(array([y1,y2]).T)
    global data1
    global data2
    results = model.fit(maxlags=l, ic='aic')
    return results.test_causality('y1', ['y2'], kind='f')['conclusion'] == 'reject'

def doMatch(uid, party):
    global receivers
    global senders

    targets = None
    selfdata = None
    if party == 'sender':
        targets = receivers
        selfdata = senders.get(uid)['data']
    elif party == 'receiver':
        targets = senders
        selfdata = receivers.get(uid)['data']
    else:
        return
        
    if selfdata is None:
        return
        
    for otherUid, targetdict in targets.items():
        targetdata = targetdict['data']
        if granger(selfdata, targetdata):
            info = {}
            info.update('other_id', otherUid)
            otherinfo = {}
            otherinfo.update('other_id', uid)
            if party == 'receiver':
                info.update('amount', targetdict['amount'])
                otherinfo.update('amount', targetdict['amount'])
            else:
                info.update('amount', senders.get(uid)['amount'])
                otherinfo.update('amount', senders.get(uid)['amount'])
            result.update(uid, info)
            result.update(otherUid, otherinfo)
            senders.pop(uid)
            receivers.pop(uid)
            senders.pop(otherUid)
            receivers.pop(otherUid)