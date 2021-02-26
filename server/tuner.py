import flask
import json
from flask import request, jsonify
from knobs import Knobs
from metrics import Metrics
from constants import *

app = flask.Flask(__name__)

@app.route('/api/v1/get_recommendation', methods=['POST'])
def json_example():
    request_data = request.get_json()
    metricsJson = json.loads(request_data[METRICS])
    knobsJson = json.loads(request_data[KNOBS])
    knobs = Knobs(vmSwapiness=knobsJson[VM_SWAPINESS])
    metrics = Metrics(throughput=metricsJson[THROUGHPUT])

    recommendedKnobs = Knobs(vmSwapiness=knobs.vmSwapiness)
    return jsonify(recommendedKnobs.serialize())

app.run(debug=True, port=8000, host='0.0.0.0')
