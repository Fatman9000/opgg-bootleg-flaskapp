import League_opgg_bootleg as lob
import json
from flask import Flask, request
app = Flask(__name__)


@app.route('/<name>', methods=["GET", "POST"])
def league_app(name):
    if request.method == "POST":
        incoming_json = request.get_json(force=True)
        if "get_match_ids" in incoming_json:
            tmp = lob.return_match_ids(name)
            return json.dumps(tmp)
        elif "get_match" in incoming_json:
            tmp = lob.display_match(incoming_json["get_match"], name)
            return json.dumps(tmp)
    if request.method == "GET":
        var = lob.pull_user_data(name)
        return var
