import pandas
import statsmodels.api
from numpy import *
from geopy.distance import vincenty
from expiringdict import ExpiringDict

data1 = None
data2 = None
senders = ExpiringDict(max_len=100, max_age_seconds=30)
receivers = ExpiringDict(max_len=100, max_age_seconds=30)
result = ExpiringDict(max_len=100, max_age_seconds=3600)
output = {}

def corr(y1, y2):
    return corrcoef(y1, y2, 0)[0][1]

def granger(y1, y2, l = 20):
    model = statsmodels.tsa.vector_ar.var_model.VAR(array([y1,y2]).T)
    global data1
    global data2
    results = model.fit(maxlags=l, ic='aic')
    return results.test_causality('y1', ['y2'], kind='f', signif=0.01)['conclusion'] == 'reject'
    
def geo_dist(g1, g2):
    coords1 = (g1['lat'], g1['lng'])
    coords2 = (g2['lat'], g2['lng'])
    return vincenty(coords1,coords2).meters

def doMatch(uid, party):
    global receivers
    global senders

    targets = None
    selfdict = None
    if party == 'sender':
        targets = receivers
        selfdict = senders.get(uid)
    elif party == 'receiver':
        targets = senders
        selfdict = receivers.get(uid)
    else:
        return
        
    if selfdict is None:
        return
        
    for otherUid, targetdict in targets.items():
        selfdata = selfdict['data']
        targetdata = targetdict['data']
        if geo_dist(selfdict['geo'], targetdict['geo']) < 1000:
            if granger(selfdata, targetdata):
                info = {}
                info['other_id'] = targetdict['id']
                otherinfo = {}
                otherinfo['other_id'] = selfdict['id']
                if party == 'receiver':
                    info['amount'] = targetdict['amount']
                    otherinfo['amount'] = targetdict['amount']
                else:
                    info['amount'] = senders.get(uid)['amount']
                    otherinfo['amount'] = senders.get(uid)['amount']
                result[uid] = info
                result[otherUid] = otherinfo
                if party == 'sender':
                    senders.pop(uid)
                    receivers.pop(otherUid)
                else:
                    senders.pop(otherUid)
                    receivers.pop(uid)
                break
        return;