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
    knobs = Knobs(vmSwapiness=knobsJson[VM_SWAPINESS])
    metrics = Metrics(throughput=metricsJson[THROUGHPUT])

    store[knobs.vmSwapiness] = metrics.throughput
    time.sleep(10)

    return jsonify(store)

@app.route('/api/v1/create_tuning_session', methods=['GET'])
def create_tuning_session():
    session_id=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    bayesian = Bayesian(session_id)
    bayesian.start()
    while len(store) == 0:
        time.sleep(SLEEP)

    return jsonify(store)

class Bayesian (threading.Thread):
   def __init__(self, sessionId):
      threading.Thread.__init__(self)
      self.threadID = sessionId
      self.name = sessionId

   def run(self):
      space = hp.uniform('vm_swapiness', 0, 100)
      best = fmin(
          fn=self.get_metrics,
          space=space,
          algo=tpe.suggest,
          max_evals=1000
      )
      LOG.info(f'best = {best}')

   def get_metrics(self, vm_swapiness):
       store[vm_swapiness] = 0
       while store[vm_swapiness] == 0:
           time.sleep(SLEEP)
       result = store[vm_swapiness]
       store.pop(vm_swapiness)
       return result

app.run(debug=True, port=8000, host='0.0.0.0')



