#!/usr/bin/env python

from datetime import datetime
from flask import Flask, request, jsonify, render_template
import pprint

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('graph.html')

app.run(host='0.0.0.0', port=5000, debug = True)
