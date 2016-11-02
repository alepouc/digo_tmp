#!/usr/bin/env python

from datetime import datetime
from flask import Flask, request, redirect, jsonify, render_template, Response, abort, send_from_directory, url_for, session, flash
from flask_login import current_user, LoginManager, UserMixin, login_required, login_user, logout_user
import time
import json
from glob import glob
import os
from collections import defaultdict
from collections import Counter
from werkzeug import secure_filename
import csv
import io


from .models import *

app = Flask(__name__)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(username):
    return User(username)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data)
        if user.find():
            flash('A user with this username already exists.', 'error')
        else:
            user.register(form.email.data, form.password.data)
            login_user(user)
            if current_user.is_authenticated:
                flash('Logged in.', 'success')
                return redirect(url_for('get_home_page'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data)
        if not user.verify_password(form.password.data):
            flash('Invalid login.', 'error')
        else:
            login_user(user)
            if current_user.is_authenticated:
                flash('Logged in.', 'success')
                return redirect(url_for('get_home_page'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Get neo4j JSON for graph
#########################################
@app.route("/get_neo4j_json_for_graph")
@login_required
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
    return jsonify(SigmaJSON)



# Get neo4j JSON for table
#########################################
@app.route("/get_neo4j_json_for_table")
@login_required
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
    return jsonify(tableJSON)




# Get all campaigns
#########################################
@app.route("/get_all_campaigns")
@login_required
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
@login_required
def get_indicators_specific_campaign_for_table_view():
    campaign = request.args.get("campaign")
    query = 'MATCH (n) WHERE n.campaign="'+campaign+'" return n'
    results = gdb.query(query, data_contents=True)
    tableJSON = convertNeo4jJsonToTable(results.graph)
    return jsonify(tableJSON)




# Get number of indicator by node type for specific campaign
#########################################
@app.route("/get_number_of_indicator_by_node_type_for_specific_campaign")
@login_required
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
@login_required
def get_all_digos():
    files = glob('digo/digos/*')
    digos = {}
    for row in files:
        if ".py" in row:
            if "__init__.py" not in row:
                digo = row.split("/")[2].split(".")[0]
                digos_import = __import__('digos', globals(), locals(), [], 1)
                func = getattr(digos_import, digo)
                returnType = func.returnType()
                for type in returnType:
                    digos.setdefault(type, []).append(digo)

    return digos



# Get digo result
#########################################
@app.route('/get_digo_result')
@login_required
def get_digo_result():
    digo = request.args.get('digo')
    value = request.args.get('value')
    type = request.args.get('type')

    conf['type'] = type
    conf['value'] = value

    digos_import = __import__('digos', globals(), locals(), [], 1)
    func = getattr(digos_import, digo)
    result = func.getResult(conf)
    return jsonify(list(result.items()))



# Get all nodes types
#########################################
@app.route("/get_all_nodes_types")
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def add_relationship():
    id1 = request.form["id1"]
    id2 = request.form["id2"]
    query = 'START a=node('+id1+'), b=node('+id2+') CREATE UNIQUE (a)-[r:relation]->(b)'
    Id = gdb.query(query)
    return "Relation created"


# Delete node
#########################################
@app.route('/delete_node', methods=['POST'])
@login_required
def delete_node():
    Id = request.form["id"]
    query = 'START n=node('+Id+') OPTIONAL MATCH (n)-[r]-() DELETE n,r'
    n = gdb.query(query)
    return "Node delete"



# Delete relationship
#########################################
@app.route('/delete_relationship', methods=['POST'])
@login_required
def delete_relationship():
    Id = request.form["id"]
    query = 'start r=rel('+Id+') delete r;'
    n = gdb.query(query)
    return "Relationship delete"




# Edit node
#########################################
@app.route('/edit_node', methods=['POST'])
@login_required
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





@app.route('/settings', methods=['GET'])
@login_required
def settings():
    try:
        return render_template('settings.html', settings=settings)
    except Exception as e:
        return render_template('error.html', error=e)



# Get home page
#########################################
@app.route('/', methods=['GET'])
@login_required
def get_home_page():
    return render_template("dashboard.html")


# Get campaigns page
#########################################
@app.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    return render_template("dashboard.html")


# Get campaigns page
#########################################
@app.route('/graph', methods=['GET'])
@login_required
def get_graph():

    # Parameters
    campaign = request.args.getlist('campaign')
    indicator = request.args.getlist('indicator')

    # Function executed by default
    digos = get_all_digos()

    if campaign:
        return render_template("graph.html", digos=digos, arg="campaign", campaign=campaign)
    if indicator:
        return render_template("graph.html", digos=digos, arg="indicator", indicator=indicator)
    else:
        return redirect(url_for('get_dashboard'))


# Get upload page
#########################################
@app.route('/upload', methods=['GET', 'POST'])
@login_required
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



@app.route('/error', methods=['GET'])
@login_required
def error():
    return render_template('error.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug = True)
