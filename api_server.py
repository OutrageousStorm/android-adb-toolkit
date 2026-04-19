#!/usr/bin/env python3
from flask import Flask, jsonify
import subprocess
app = Flask(__name__)

@app.route("/info", methods=["GET"])
def info():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=8000)
