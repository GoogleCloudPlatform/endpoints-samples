# Copyright 2019, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json

from flask import abort
from flask import Flask
from flask import g
from flask import jsonify
from flask import request
from google.cloud import datastore
from werkzeug.local import LocalProxy

app = Flask(__name__)

VEHICLE_KIND = "vehicle"
NOTE_KIND = "note"


def get_datastore_client():
    if "datastore" not in g:
        g.datastore = datastore.Client()
    return g.datastore


datastore_client = LocalProxy(get_datastore_client)


@app.before_request
def require_user_email():
    header = request.headers.get("X-Endpoint-API-UserInfo")
    if header is None:
        abort(403)
    val = json.loads(base64.b64decode(header))
    # the full JWT claims are available as json.loads(val['claims'])
    # however, the email will be in the outer value, if one was provided
    if "email" not in val:
        abort(403)
    g.email = val["email"]


@app.route("/vehicles", methods=["GET"])
def my_vehicles():
    query = datastore_client.query(kind=VEHICLE_KIND)
    query.add_filter("owner", "=", g.email)
    return jsonify([e["plate"] for e in query.fetch()])


@app.route("/vehicle", methods=["POST"])
def add_vehicle():
    json_data = request.get_json()
    plate = json_data["plate"]
    entity = datastore.Entity(key=datastore_client.key(VEHICLE_KIND, plate))
    entity["plate"] = plate
    entity["owner"] = g.email
    datastore_client.put(entity)
    return jsonify({})


@app.route("/vehicle/<plate>", methods=["GET"])
def see_vehicle(plate):
    key = datastore_client.key(VEHICLE_KIND, plate)
    vehicle = datastore_client.get(key)
    if vehicle is None:
        abort(404)
    if vehicle["owner"] != g.email:
        # This does leak the existence of the vehicle, but for this example, that's not too bad
        abort(403)

    query = datastore_client.query(kind=NOTE_KIND)
    query.add_filter("plate", "=", plate)
    return jsonify([e["note"] for e in query.fetch()])


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
