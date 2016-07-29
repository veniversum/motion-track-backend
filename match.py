import pandas
import statsmodels.api
from numpy import *
from flask import json
from flask import Flask, request
from flask import render_template
from flask import jsonify
app = Flask(__name__)

data1 = None
data2 = None
result = {}

@app.route('/granger/', methods=['POST'])
def process():
    content = request.get_json(silent=True)
    y1 = content['y1']
    y2 = content['y2']
    try:
        result = granger(y1, y2)
        correff = corr(y1, y2)
        return jsonify({"granger_match":result, "corrcoef":correff})
    except Exception, e:
        return jsonify({"granger_match":False, "corrcoef":0})

@app.route('/log/', methods=['POST'])
def logging():
    data = request.get_json(silent=True)['data']
    print data
    global data1
    global data2
    global result
    if data1 is None:
        data1 = data
    elif data2 is None:
        data2 = data
        result.update({"correff":corr(data1, data2)})
        result.update({"granger_match":granger(data1, data2)})
        result.update({"data1":data1})
        result.update({"data2":data2})
    else:
        data1 = data
        data2 = None
    return ''

@app.route('/status/', methods=['GET'])
def status():
    global result
    return jsonify(result)

def corr(y1, y2):
    return corrcoef(y1, y2)[0][1]

def granger(y1, y2):
    model = statsmodels.tsa.vector_ar.var_model.VAR(array([y1,y2]).T)
    global data1
    global data2
    results = model.fit(20)
    return results.test_causality('y1', ['y2'], kind='wald')['conclusion'] == 'reject'

if __name__ == '__main__':
    app.run(host= '0.0.0.0')