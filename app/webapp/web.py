#!/usr/bin/env python

from datetime import datetime
from flask import Flask, request, jsonify, render_template
from py2neo import Graph

app = Flask(__name__)

graph = Graph(host='digo-db', user='neo4j', password='debug')

@app.route('/')
def index():
#    a = graph.run('MATCH (n) RETURN n')
#    for i in a:
#        print(i)
    return render_template('graph.html')

@app.route('/data.json')
def datajson():
    return '''{
  "nodes": [
    {
      "id": "n0",
      "label": "A node TOTO",
      "x": 0,
      "y": 0,
      "size": 3
    },
    {
      "id": "n1",
      "label": "Another node",
      "x": 3,
      "y": 1,
      "size": 2
    },
    {
      "id": "n2",
      "label": "And a last one",
      "x": 1,
      "y": 3,
      "size": 1
    }
  ],
  "edges": [
    {
      "id": "e0",
      "source": "n0",
      "target": "n1"
    },
    {
      "id": "e1",
      "source": "n1",
      "target": "n2"
    },
    {
      "id": "e2",
      "source": "n2",
      "target": "n0"
    }
  ]
}'''


app.run(host='0.0.0.0', port=5000, debug = True)
