import League_opgg_bootleg as lob
import json
from flask import Flask, request
app = Flask(__name__)


@app.route('/<name>', methods=["GET", "POST"])
def hello_world(name):
    if request.method == "POST":
        incoming_json = request.get_json(force=True)
        if incoming_json["get_match_ids"]:
            tmp = lob.return_match_ids(name)
            return json.dumps(tmp)
    if request.method == "GET":
        var = lob.pull_user_data(name)
        return var
