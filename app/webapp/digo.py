#!/usr/bin/env python

from datetime import datetime
from flask import Flask, request, redirect, jsonify, render_template, Response, abort, send_from_directory
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
from werkzeug import secure_filename
import csv
import io


app = Flask(__name__)
gdb = GraphDatabase("http://digo-db:7474/db/data", username="neo4j", password="debug")
app.jinja_env.autoescape = False
app.config["JSON_SORT_KEYS"] = False
ALLOWED_EXTENSIONS = set(['csv'])
UPLOAD_FOLDER = '/upload_tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
                if tmp not in data:
                    data.append(tmp)
    return jsonify(data)



# Get neo4j JSON for graph
#########################################
@app.route("/get_neo4j_json_for_graph")
def get_neo4j_json_for_graph():

    if request.args.getlist('campaign'):
        arg = ""
        campaigns = request.args.getlist('campaign')
        for i in range(0, len(campaigns)):
            if i == (len(campaigns)-1):
                arg += 'n.campaign="'+campaigns[i]+'"'
            else:
                arg += 'n.campaign="'+campaigns[i]+'" OR '
        query = 'MATCH (n) WHERE '+arg+'  OPTIONAL MATCH (n)-[r]-() RETURN n, r'

    elif request.args.getlist('indicator'):
        arg = []
        indicators = request.args.getlist('indicator')
        for i in range(0, len(indicators)):
            arg.append(int(indicators[i]))
        query = 'MATCH (n) WHERE ID(n) IN '+str(arg)+' OPTIONAL MATCH (n)-[r]-() RETURN n,r'

    else:
        query = 'MATCH (n) OPTIONAL MATCH (n)-[r]-() RETURN n, r LIMIT 50'

    results = gdb.query(query, data_contents=True)
    SigmaJSON = convertNeo4jJsonToSigma(results.graph)
    return SigmaJSON



# Get neo4j JSON for table
#########################################
@app.route("/get_neo4j_json_for_table")
def get_neo4j_json_for_table():
    if request.args.getlist('campaign'):
        arg = ""
        campaigns = request.args.getlist('campaign')
        for i in range(0, len(campaigns)):
            if i == (len(campaigns)-1):
                arg += 'n.campaign="'+campaigns[i]+'"'
            else:
                arg += 'n.campaign="'+campaigns[i]+'" OR '
        query = 'MATCH (n) WHERE '+arg+'  OPTIONAL MATCH (n)-[r]-() RETURN n, r'

    if request.args.getlist('indicator'):
        arg = []
        indicators = request.args.getlist('indicator')
        for i in range(0, len(indicators)):
            arg.append(int(indicators[i]))
        query = 'MATCH (n) WHERE ID(n) IN '+str(arg)+' OPTIONAL MATCH (n)-[r]-() RETURN n,r'

    else:
        query = 'MATCH (n) OPTIONAL MATCH (n)-[r]-() RETURN n, r LIMIT 50'

    results = gdb.query(query, data_contents=True)
    tableJSON = convertNeo4jJsonToTable(results.graph)
    return tableJSON




# Get all campaigns
#########################################
@app.route("/get_all_campaigns")
def get_all_campaigns():
    campaigns = {}
    query = 'MATCH (n) return distinct n.campaign'
    results = gdb.query(query, data_contents=True)
    for row in results.rows:
        campaigns[row[0]] = row[0]
    return jsonify(campaigns)



# Get indicators for specific campaign for table view
#########################################
@app.route("/get_indicators_specific_campaign_for_table_view", methods=['GET'])
def get_indicators_specific_campaign_for_table_view():
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
    return jsonify(list(result.items()))



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

    query = 'START n=node(*) WHERE n.type = "'+Value+'" return n'
    results = gdb.query(query, data_contents=True)

    if results:
        for row in results.rows:
            return "The node is already present in the database"
    else:
        new_node = gdb.nodes.create(type=Value, confidence=Confidence, diamond_model=Diamond_model, campaign=Campaign, first_seen=FirstSeen, last_seen=LastSeen, tags=Tags, comments=Comments)
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



# Delete relationship
#########################################
@app.route('/delete_relationship', methods=['POST'])
def delete_relationship():
    Id = request.form["id"]
    query = 'start r=rel('+Id+') delete r;'
    n = gdb.query(query)
    return "Relationship delete"




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
@app.route('/dashboard')
def get_campaigns_page():
    campaign = request.args.getlist('campaign')
    indicator = request.args.getlist('indicator')
    if campaign:
        return render_template("graph.html", arg="campaign", campaign=campaign)
    if indicator:
        return render_template("graph.html", arg="indicator", indicator=indicator)
    else:
        return render_template("dashboard.html")




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



# Get upload page
#########################################
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    names = []
    if request.method == 'POST':
        node_already_present = []
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            data = list(csv_input)
            for row in range(0, len(data)):
                output = {}
                if row == 0:
                    if 'type' not in data[row] or 'value' not in data[row]:
                        return render_template("upload.html", message='The type field or value field has not been found !')
                    else:
                        names = data[row]
                else:
                    for column in range(0, len(data[row])):
                        if names[column] == "type":
                            Value = data[row][column]
                        elif names[column] == "value":
                            output['type'] = data[row][column]
                        else:
                            output[names[column]] = data[row][column]

                    if 'confidence' not in data[row]:
                        output['confidence'] = 'NULL'
                    if 'diamondmodel' not in data[row]:
                        output['diamondmodel'] = 'NULL'
                    if 'campaign' not in data[row]:
                        output['campaign'] = 'NULL'
                    if 'firstseen' not in data[row]:
                        output['firstseen'] = 'NULL'
                    if 'lastseen' not in data[row]:
                        output['lastseen'] = 'NULL'
                    if 'tags' not in data[row]:
                        output['tags'] = 'NULL'
                    if 'comments' not in data[row]:
                        output['comments'] = 'NULL'

                    query = 'START n=node(*) WHERE n.type = "'+output['type']+'" return n'
                    results = gdb.query(query, data_contents=True)

                    if results:
                        node_already_present.append(output['type'])
                    else:
                        new_node = gdb.nodes.create(**output)
                        new_node.labels.add(Value)

        if len(node_already_present) > 0:
            return render_template("upload.html", message='Some node(s) already exist in the database', node_already_present=node_already_present)
        else:
            return render_template("upload.html", message='success')
    else:
        return render_template("upload.html")






if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug = True)
