import uuid
import time
from match import *
from flask import json
from flask import Flask, request
from flask import render_template
from flask import jsonify

app = Flask(__name__)

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
    global output
    if data1 is None:
        data1 = data
    elif data2 is None:
        data2 = data
        output.update({"correff":corr(data1, data2)})
        output.update({"granger_match":granger(data1, data2)})
        output.update({"data1":data1})
        output.update({"data2":data2})
    else:
        data1 = data
        data2 = None
    return ''
    
@app.route('/send/', methods=['POST'])
@app.route('/send/<uid>', methods=['GET'])
def send(uid=None):
    if request.method == 'POST':
        uid = str(uuid.uuid4())
        senders[uid] = {'data': request.get_json(silent=True)['data'], 'amount': request.get_json(silent=True)['amount'], 'id': request.get_json(silent=True)['id'], 'geo': request.get_json(silent=True)['geo']}
        doMatch(uid, 'sender')
        return jsonify({'uid':uid})
    elif request.method == 'GET' and uid is not None:
        if uid in result:
            return jsonify({'uid':uid, 'status':'success', 'data': result.get(uid)})
        elif uid in senders:
            return jsonify({'uid':uid, 'status':'pending'})
        else:
            return jsonify({'uid':uid, 'status':'invalid_or_expired'})

@app.route('/receive/', methods=['POST'])
@app.route('/receive/<uid>', methods=['GET'])
def receive(uid=None):
    if request.method == 'POST':
        uid = str(uuid.uuid4())
        receivers[uid] = {'data':request.get_json(silent=True)['data'], 'id': request.get_json(silent=True)['id'], 'geo': request.get_json(silent=True)['geo']}
        doMatch(uid, 'receiver')
        return jsonify({'uid':uid})
    elif request.method == 'GET' and uid is not None:
        if uid in result:
            return jsonify({'uid':uid, 'status':'success', 'data': result.get(uid)})
        elif uid in receivers:
            return jsonify({'uid':uid, 'status':'pending'})
        else:
            return jsonify({'uid':uid, 'status':'invalid_or_expired'})


@app.route('/status/', methods=['GET'])
def status():
    global output
    return jsonify(output)

@app.route('/rerun/<int:fit>', methods=['GET'])
def rerun(fit):
    global output
    global data1
    global data2
    output.update({"correff":corr(data1, data2)})
    output.update({"granger_match":granger(data1, data2, fit)})
    return jsonify(output)
    
if __name__ == '__main__':
    app.run(host= '0.0.0.0')