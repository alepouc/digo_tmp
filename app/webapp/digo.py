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
from collections import Counter



app = Flask(__name__)
gdb = GraphDatabase("http://digo-db:7474/db/data", username="neo4j", password="debug")
app.jinja_env.autoescape = False


def convertNeo4jJsonToSigma(neo4jJson):

    '''
    test = [{
            "id": "test",
            "label": "label",
            "type": "type",
            "confidence": "confidence",
            "diamond_model": "diamond_model",
            "campaign": "campaign",
            "relations": "relations",
            "first_seen": "first_seen",
            "last_seen":  "last_seen"
            }]
    '''


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
        item['label'] = item.pop("labels")
        Properties = item['properties']
        Label = item['label']
        item['label'] = Properties['type']
        item['properties']['type'] = Label[0]


    for item in SigmaJSON["edges"]:
        item['source'] = item.pop("startNode")
        item['target'] = item.pop("endNode")

    return jsonify(SigmaJSON)




def convertNeo4jJsonToTable(neo4jJson):

    data = []

    for row in neo4jJson:
        for d in row['nodes']:
            tmp = {}
            for k in d:
                if k == 'id':
                     tmp['id'] = d[k]
                if k == 'labels':
                    tmp['type'] = d[k][0]
                if k == 'properties':
                    for key in d[k]:
                        if key == 'type':
                            tmp['value'] = d[k][key]
                        else:
                            tmp[key] = d[k][key]
            data.append(tmp)

    return jsonify(data)



@app.route('/')
def get_homepage():
    '''
    Default template
    '''
    number_of_indicator_by_type = get_number_of_indicator_by_type()
    return render_template("dashboard.html", number_of_indicator_by_type=number_of_indicator_by_type)




@app.route('/graph.html')
def get_graphpage():
    return render_template("graph.html")




@app.route("/neo4jJson")
def get_neo4jJson():
    '''
    Get Neo4j JSON
    '''
    query = 'MATCH (n) OPTIONAL MATCH (n)-[r]-() return n,r'
    results = gdb.query(query, data_contents=True)
    SigmaJSON = convertNeo4jJsonToSigma(results.graph)
    return SigmaJSON



@app.route("/table_nodes")
def get_table_nodes():
    query = 'MATCH (n) RETURN n'
    results = gdb.query(query, data_contents=True)
    tableJSON = convertNeo4jJsonToTable(results.graph)
    return tableJSON



@app.route('/add_node', methods=['POST'])
def add_node():
    Type = request.form["type"]
    Value = request.form["value"]
    new_node = gdb.nodes.create(type=Value)
    new_node.labels.add(Type)
    return str(new_node.id)




@app.route('/add_property', methods=['POST'])
def add_node_properties():
    Id = request.form['id']
    Property_key = request.form['property_key']
    Property_value = request.form['property_value']
    n = gdb.nodes.get(Id)
    n.set(Property_key, Property_value)
    return "Property added to the node"




@app.route('/edit_node', methods=['POST'])
def edit_node():
    data = request.form
    Id = data['id']
    Type = data['value']
    Label = data['type']

    n = gdb.nodes.get(Id)

    # Remove current propertiies
    for row in n.properties:
        query = 'START n=node('+Id+') REMOVE n.'+row
        n = gdb.query(query)

    # Insert new properties
    for key, value in data.items():
        if key == 'id':
            pass
        elif key == 'value':
            query = 'START n=node('+Id+') SET n.type = "'+Type+'"'
            n = gdb.query(query)
        else:
            query = 'START n=node('+Id+') SET n.'+key+' = "'+value+'"'
            n = gdb.query(query)

        #query = 'START n=node('+Id+') REMOVE n.'+row
        # = gdb.query(query)

    # Get current labels name
    query = 'START n=node('+Id+') return labels(n)'
    labels = gdb.query(query)
    for row in labels:
        label = row[0][0]

    # Remove current label
    query = 'START n=node('+Id+') REMOVE n:'+label
    n = gdb.query(query)

    # Add new label
    query = 'START n=node('+Id+') set n:'+Label
    n = gdb.query(query)

    return "Node updated"





@app.route('/delete_node', methods=['POST'])
def delete_node():
    Id = request.form["id"]
    query = 'START n=node('+Id+') OPTIONAL MATCH (n)-[r]-() DELETE n,r'
    n = gdb.query(query)
    return "Node delete"




@app.route('/add_relationship', methods=['POST'])
def add_relationship():
    id1 = request.form["id1"]
    id2 = request.form["id2"]
    query = 'START a=node('+id1+'), b=node('+id2+') CREATE UNIQUE (a)-[r:relation]->(b)'
    Id = gdb.query(query)
    return "Relation created"



@app.route('/get_all_actions')
def get_all_actions():
    files = glob('actions/*')
    result_json = defaultdict(list)
    for row in files:
        if ".py" in row:
            if "__init__.py" not in row:
                action_type = row.split("_")[0].split("/")[1]
                action = row.split("/")[1].split(".")[0]
                result_json[action_type].append(action)
    return jsonify(result_json)




@app.route("/get_all_types")
def get_all_types():
    '''
    Get available type
    '''
    output = {}
    query = 'START n=node(*) RETURN distinct labels(n)'
    results = gdb.query(query, data_contents=True)
    for row in results.rows:
        output[row[0][0]]=row[0][0].lower()
    return jsonify(output)



@app.route("/get_number_of_indicator_by_type")
def get_number_of_indicator_by_type():
    '''
    Get available type
    '''
    output = []
    query = 'START n=node(*) RETURN labels(n)'
    results = gdb.query(query, data_contents=True)
    for row in results.rows:
        output.append(row[0][0])
    c = Counter(output)
    return dict(c)



@app.route('/action')
def get_actions():
    action = request.args.get('action')
    input = request.args.get('input')
    actions_import = __import__('actions')
    func = getattr(actions_import, action)
    result = func.getResult(input)
    output = {}
    output["json_result"] = result
    return jsonify(output)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug = True)
