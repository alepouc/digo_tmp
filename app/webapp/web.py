#!/usr/bin/env python

from datetime import datetime
from flask import Flask, request, jsonify, render_template, Response
from neo4jrestclient.client import GraphDatabase
import time
import json
from pprint import pprint
from glob import glob
import os
import random
from collections import defaultdict
from actions import *


app = Flask(__name__)
gdb = GraphDatabase("http://digo-db:7474/db/data", username="neo4j", password="debug")



def convertNeo4jJsonToSigma(neo4jJson):
    '''
    Convert Neo4j JSON to Sigma JSON
    '''

    nodes_j = []
    edges_j = []

    for row in neo4jJson:
        if str(row['relationships']) != "[]":
            edges_j.extend(row['relationships'])
        nodes_j.extend(row['nodes'])

    nodes_j = {"nodes": nodes_j}
    edges_j = {"edges": edges_j}

    nodes = []
    for item in nodes_j['nodes']:
        if item not in nodes:
            nodes.append(item)


    edges = []
    for item in edges_j['edges']:
        if item not in edges:
            edges.append(item)

    SigmaJSON = {
                "nodes": nodes,
                "edges" : edges }


    for item in SigmaJSON["nodes"]:
        item['x'] = random.random()
        item['y'] = random.random()


    for item in SigmaJSON["edges"]:
        item['source'] = item.pop("startNode")
        item['target'] = item.pop("endNode")

    return jsonify(SigmaJSON)





@app.route('/')
def get_homepage():
    '''
    Default template
    '''
    return render_template("index.html")



@app.route('/graph.html')
def get_graphpage():
    return render_template("graph.html")



@app.route("/neo4jJson")
def get_neo4jJson():
    '''
    Get Neo4j JSON
    '''
    #query = 'MATCH p=shortestPath( (bacon:Person {name:"Kevin Bacon"})-[*]-(meg:Person {name:"Meg Ryan"}) ) RETURN p'
    #query = 'MATCH (people:Person)-[relatedTo]-(:Movie {title: "Cloud Atlas"}) RETURN people.name, Type(relatedTo), relatedTo'
    #query = 'MATCH (n) RETURN n'
    query = 'MATCH (n)-[r]-(m) RETURN n, r, m limit 20'
    results = gdb.query(query, data_contents=True)
    if results:
        SigmaJSON = convertNeo4jJsonToSigma(results.graph)
        return SigmaJSON
    else:
        return "Error"



@app.route('/getActionListing')
def getActionListing():
    files = glob('actions/*')
    result_json = defaultdict(list)

    for row in files:
        action_type = row.split("_")[0].split("/")[1]
        action = row.split("_")[1]
        result_json[action_type].append(action)
    return jsonify(result_json)



@app.route('/action')
def get_actions():
    action = request.args.get('action')
    input = request.args.get('input')
    result = domain_whois.whois(input)
    result = '{"json_result":['+str(result)+']}'
    return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug = True)
