#!/usr/bin/env python

from neo4jrestclient.client import GraphDatabase
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import random
from passlib.hash import bcrypt


gdb = GraphDatabase("http://digo-db:7474/db/data", username="neo4j", password="debug")


conf = {
            'type':'',
            'value': '',
            'username':'',
            'password':'',
            'api':''
        }



class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])



class User:
    def __init__(self, username):
        self.username = username.lower()
        self.email = None
        self.password = None

    def find(self):
        query = 'START n=node(*) WHERE n.username = "'+self.username+'" and labels(n) = "user" return n'
        user = gdb.query(query, data_contents=True)
        return user

    def register(self, email, password):
        new_node = gdb.nodes.create(username=self.username, email=email, password=bcrypt.encrypt(password))
        new_node.labels.add('user')
        return True

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user.rows[0][0]['password'])
        else:
            return False

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_active(self):
        """True, as all users are active."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False







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
    return SigmaJSON




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
    return data



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Add user
#########################################
def add_user(user):
    #print(user.username)
    #print(user.email)
    #print(user.password)

    #query = 'START n=node(*) WHERE n.type = "'+Value+'" return n'
    #results = gdb.query(query, data_contents=True)

    #if results:
    #    for row in results.rows:
    #        return "The node is already present in the database"
    #else:
    #    new_node = gdb.nodes.create(type=Value, confidence=Confidence, diamond_model=Diamond_model, campaign=Campaign, first_seen=FirstSeen, last_seen=LastSeen, tags=Tags, comments=Comments)
    #    new_node.labels.add(Type)
    #    return str(new_node.id)
    return "ok"
