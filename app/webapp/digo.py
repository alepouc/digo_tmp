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
from digos import *
from collections import Counter



app = Flask(__name__)
gdb = GraphDatabase("http://digo-db:7474/db/data", username="neo4j", password="debug")
app.jinja_env.autoescape = False


# Convert Neo4j JSON to Sigma JSON
#########################################
def convertNeo4jJsonToSigma(neo4jJson):
    nodes_j = []
    edges_j = []
    if neo4jJson:
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

    else:
        SigmaJSON = {"nodes": [], "edges": []}
    return jsonify(SigmaJSON)




# Convert Neo4j JSON to Json table
#########################################
def convertNeo4jJsonToTable(neo4jJson):
    data = []
    if neo4jJson:
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



# Get neo4j JSON for graph
#########################################
@app.route("/get_neo4j_json_for_graph")
def get_neo4j_json_for_graph():
    query = 'MATCH (n) OPTIONAL MATCH (n)-[r]-() return n,r'
    results = gdb.query(query, data_contents=True)
    SigmaJSON = convertNeo4jJsonToSigma(results.graph)
    return SigmaJSON


# Get neo4j JSON for table
#########################################
@app.route("/get_neo4j_json_for_table")
def get_neo4j_json_for_table():
    query = 'MATCH (n) RETURN n'
    results = gdb.query(query, data_contents=True)
    tableJSON = convertNeo4jJsonToTable(results.graph)
    return tableJSON



# Get all campaigns
#########################################
@app.route("/get_all_campaigns")
def get_all_campaigns():
    campaigns = []
    query = 'MATCH (n) return distinct n.campaign'
    results = gdb.query(query, data_contents=True)
    for row in results.rows:
        campaigns.append({"campaign": row[0]})
    return jsonify(campaigns)



# Get indicators for specific campaign
#########################################
@app.route("/get_indicators_specific_campaign", methods=['GET'])
def get_indicators_specific_campaign():
    campaign = request.args.get("campaign")
    query = 'MATCH (n) WHERE n.campaign="'+campaign+'" return n'
    results = gdb.query(query, data_contents=True)
    tableJSON = convertNeo4jJsonToTable(results.graph)
    return tableJSON


# Get number of indicator by node type for specific campaign
#########################################
@app.route("/get_number_of_indicator_by_node_type_for_specific_campaign")
def get_number_of_indicator_by_node_type_for_specific_campaign():
    campaign = request.args.get("campaign")
    output = []
    query = 'START n=node(*) WHERE n.campaign="'+campaign+'" RETURN labels(n)'
    results = gdb.query(query, data_contents=True)
    if results:
        for row in results.rows:
            output.append(row[0][0])
        c = Counter(output)
    else:
        c = {}
    return jsonify(dict(c))



# Get all digos
#########################################
@app.route('/get_all_digos')
def get_all_digos():
    files = glob('digos/*')
    result_json = defaultdict(list)
    for row in files:
        if ".py" in row:
            if "__init__.py" not in row:
                action_type = row.split("_")[0].split("/")[1]
                action = row.split("/")[1].split(".")[0]
                result_json[action_type].append(action)
    return jsonify(result_json)


# Get digo result
#########################################
@app.route('/get_digo_result')
def get_digo_result():
    digo = request.args.get('digo')
    input = request.args.get('input')
    digos_import = __import__('digos')
    func = getattr(digos_import, digo)
    result = func.getResult(input)
    output = {}
    output["json_result"] = result
    return jsonify(output)



# Get all nodes types
#########################################
@app.route("/get_all_nodes_types")
def get_all_nodes_types():
    Type = {
            "ipv4": "ipv4",
            "ipv6": "ipv6",
            "domain": "domain",
            "url": "url",
            "email": "email",
            "hash": "hash",
            "country": "country",
            "entity": "entity",
            "threat_actor": "threat_actor"
        }

    query = 'START n=node(*) RETURN distinct labels(n)'
    results = gdb.query(query, data_contents=True)
    if results:
        for row in results.rows:
            if row[0][0].lower() not in Type.values():
                Type[row[0][0]]=row[0][0].lower()

    return jsonify(Type)


# Get number of indicator by node type
#########################################
@app.route("/get_number_of_indicator_by_node_type")
def get_number_of_indicator_by_node_type():
    output = []
    query = 'START n=node(*) RETURN labels(n)'
    results = gdb.query(query, data_contents=True)
    if results:
        for row in results.rows:
            output.append(row[0][0])
        c = Counter(output)
    else:
        c = {}
    return dict(c)


# Add node
#########################################
@app.route('/add_node', methods=['POST'])
def add_node():
    Type = request.form["type"]
    Value = request.form["value"]

    Confidence = request.form["confidence"]
    if Confidence == "":
        Confidence = "NULL"

    Diamond_model = request.form["diamondmodel"]
    if Diamond_model == "":
        Diamond_model = "NULL"

    Campaign = request.form["campaign"]
    if Campaign == "":
        Campaign  = "NULL"

    FirstSeen = request.form["firstseen"]
    if FirstSeen == "":
        FirstSeen = "NULL"

    LastSeen = request.form["lastseen"]
    if LastSeen == "":
        LastSeen = "NULL"

    Tags = request.form["tags"]
    if Tags == "":
        Tags = "NULL"

    Comments = request.form["comments"]
    if Comments == "":
        Comments = "NULL"

    new_node = gdb.nodes.create(type=Value, confidence=Confidence, diamond_model= Diamond_model, campaign=Campaign, first_seen=FirstSeen, last_seen=LastSeen, tags=Tags, comments=Comments)
    new_node.labels.add(Type)
    return str(new_node.id)



# Add property
#########################################
@app.route('/add_property', methods=['POST'])
def add_node_properties():
    Id = request.form['id']
    Property_key = request.form['propertykey']
    Property_value = request.form['propertyvalue']
    n = gdb.nodes.get(Id)
    n.set(Property_key, Property_value)
    return "Property added to the node"


# Add relationship
#########################################
@app.route('/add_relationship', methods=['POST'])
def add_relationship():
    id1 = request.form["id1"]
    id2 = request.form["id2"]
    query = 'START a=node('+id1+'), b=node('+id2+') CREATE UNIQUE (a)-[r:relation]->(b)'
    Id = gdb.query(query)
    return "Relation created"


# Delete node
#########################################
@app.route('/delete_node', methods=['POST'])
def delete_node():
    Id = request.form["id"]
    query = 'START n=node('+Id+') OPTIONAL MATCH (n)-[r]-() DELETE n,r'
    n = gdb.query(query)
    return "Node delete"


# Edit node
#########################################
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




# Get home page
#########################################
@app.route('/')
def get_home_page():
    return render_template("dashboard.html")


# Get campaigns page
#########################################
@app.route('/dashboard.html')
def get_campaigns_page():
    return render_template("dashboard.html")

# Get graph page
#########################################
@app.route('/graph.html')
def get_graph_page():
    return render_template("graph.html")


# Get indicators page
#########################################
@app.route('/indicators.html')
def get_indicators_page():
    number_of_indicator_by_type = get_number_of_indicator_by_type()
    if number_of_indicator_by_type:
        return render_template("indicators.html", number_of_indicator_by_type=number_of_indicator_by_type)
    else:
        return render_template("empty.html")




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug = True)
