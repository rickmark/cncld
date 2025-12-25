from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/api/list")
@app.route("/api/list/<string:item>")
def list_endpoint(item=None):
    if item:
        # Query CouchDB for documents where title contains the item
        try:
            url = 'http://127.0.0.1:5984/cncld/_find'
            data = {
                "selector": {
                    "title": {
                        "$regex": f"(?i).*{item}.*"
                    }
                }
            }
            auth = None
            user = os.getenv('COUCHDB_USER')
            password = os.getenv('COUCHDB_PASS')
            if user and password:
                auth = (user, password)
            response = requests.post(url, json=data, auth=auth)
            data = response.json()
            # For debugging, return the full CouchDB response
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        return jsonify({"results": []})