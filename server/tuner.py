import hashlib
import string
import threading
import time
import flask
import sys
import json
import random
import logging
from flask import request, jsonify
from knobs import Knobs
from metrics import Metrics
from constants import *
from hyperopt import fmin, tpe, hp

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
Formatter = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")  # pylint: disable=invalid-name

# print the log
ConsoleHandler = logging.StreamHandler(sys.stdout)  # pylint: disable=invalid-name
ConsoleHandler.setFormatter(Formatter)
LOG.addHandler(ConsoleHandler)

store = {}
app = flask.Flask(__name__)

@app.route('/api/v1/get_recommendation', methods=['POST'])
def get_recommendation():
    request_data = request.get_json()
    metricsJson = json.loads(request_data[METRICS])
    knobsJson = json.loads(request_data[KNOBS])
    knobs = Knobs(vmSwapiness=knobsJson[VM_SWAPINESS], vmDirtyBackgroundRatio=knobsJson[VM_DIRTY_BACKGROUND_RATIO],
                  vmDirtyRatio=knobsJson[VM_DIRTY_RATIO], vmOvercommitRatio=knobsJson[VM_OVERCOMMIT_RATIO])
    metrics = Metrics(throughput=metricsJson[THROUGHPUT])
    temp = {}
    temp[VM_SWAPINESS] = knobs.vmSwapiness
    temp[VM_DIRTY_BACKGROUND_RATIO] = knobs.vmDirtyBackgroundRatio
    temp[VM_DIRTY_RATIO] = knobs.vmDirtyRatio
    temp[VM_OVERCOMMIT_RATIO] = knobs.vmOvercommitRatio
    tempJson = json.dumps(temp)
    store[tempJson] = metrics.throughput
    firstHash = int(hashlib.sha256(str(tempJson).encode('utf-8')).hexdigest(), 16) % 10 ** 8
    result = str(list(store.keys())[0])
    finalHash = int(hashlib.sha256(result.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    while firstHash == finalHash:
        time.sleep(SLEEP)
        result = str(list(store.keys())[0])
        finalHash = int(hashlib.sha256(result.encode('utf-8')).hexdigest(), 16) % 10 ** 8

    return jsonify(result)

@app.route('/api/v1/create_tuning_session', methods=['GET'])
def create_tuning_session():
    session_id=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    bayesian = Bayesian(session_id)
    bayesian.start()
    while len(store) == 0:
        time.sleep(SLEEP)
    result = next(iter(store))
    return jsonify(str(result))

class Bayesian (threading.Thread):
   def __init__(self, sessionId):
      threading.Thread.__init__(self)
      self.threadID = sessionId
      self.name = sessionId

   def run(self):
      space = {
          VM_SWAPINESS: hp.randint(VM_SWAPINESS, 100),
          VM_DIRTY_BACKGROUND_RATIO: hp.randint(VM_DIRTY_BACKGROUND_RATIO, 100),
          VM_DIRTY_RATIO: hp.randint(VM_DIRTY_RATIO, 100),
          VM_OVERCOMMIT_RATIO: hp.randint(VM_OVERCOMMIT_RATIO, 100)
      }

      best = fmin(
          fn=self.get_metrics,
          space=space,
          algo=tpe.suggest,
          max_evals=100
      )
      LOG.info(f'best = {best}')

   def get_metrics(self, parameters):
       temp = {}
       temp[VM_SWAPINESS] = int(parameters[VM_SWAPINESS])
       temp[VM_DIRTY_BACKGROUND_RATIO] = int(parameters[VM_DIRTY_BACKGROUND_RATIO])
       temp[VM_DIRTY_RATIO] = int(parameters[VM_DIRTY_RATIO])
       temp[VM_OVERCOMMIT_RATIO] = int(parameters[VM_OVERCOMMIT_RATIO])
       tempJson = json.dumps(temp)
       store[tempJson] = 0
       while store[tempJson] == 0:
           time.sleep(SLEEP)
       result = store[tempJson]
       store.pop(tempJson)
       return -1.0 * result

app.run(debug=True, port=8000, host='0.0.0.0')

