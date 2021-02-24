import flask
from flask import request, jsonify

app = flask.Flask(__name__)

@app.route('/api/v1/get_recommendation', methods=['POST'])
def json_example():
    request_data = request.get_json()
    return jsonify(request_data)

app.run(debug=True, port=8000)
