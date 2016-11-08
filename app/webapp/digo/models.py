#!/usr/bin/env python

from neo4jrestclient.client import GraphDatabase
from wtforms import Form, BooleanField, StringField, PasswordField, validators, Field
import random
from passlib.hash import bcrypt
from glob import glob

ALLOWED_EXTENSIONS = set(['csv'])


gdb = GraphDatabase("http://digo-db:7474/db/data", username="neo4j", password="debug")


conf = {
            'type':'',
            'value': '',
            'username':'',
            'password':'',
            'api':''
        }



class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=2, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])
    remember_me = BooleanField('remember_me', default=False)



class ProfileForm(Form):
    currentpassword = PasswordField('Old Password', [validators.DataRequired()])
    newpassword = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class SettingsForm(Form):
    pass


class TitleField(Field):
    def _value(self):
        if self.data:
            return self.data
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]


class User:
    def __init__(self, username):
        self.username = username.lower()
        self.email = None
        self.password = None
        self.settings = {}
        query = 'START n=node(*) WHERE n.username = "'+self.username+'" and labels(n) = "user" return n'
        user = gdb.query(query, data_contents=True)
        if user:
            if 'email' in user.rows[0][0]:
                self.email = user.rows[0][0]['email']
            if 'password' in user.rows[0][0]:
                self.password = user.rows[0][0]['password']
            if 'settings' in user.rows[0][0]:
                self.settings = user.rows[0][0]['settings']

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return str(self.username)

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_active(self):
        """True, as all users are active."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def find(self):
        if self.email != None:
            return True
        else:
            return False

    def register(self, email, password):
        settings = self.set_default_settings()
        new_node = gdb.nodes.create(username=self.username, email=email, password=bcrypt.encrypt(password), settings=str(settings))
        new_node.labels.add('user')
        return True

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, self.password)
        else:
            return False

    def update_password(self, password):
        query = 'MATCH (n) WHERE n.username="'+self.username+'" SET n.password="'+bcrypt.encrypt(password)+'"'
        n = gdb.query(query)
        return True

    def set_default_settings(self):
        files = glob('digo/digos/*')
        settings = {}
        for row in files:
            if ".py" in row:
                if "__init__.py" not in row:
                    digo = row.split("/")[2].split(".")[0]
                    digos_import = __import__('digos', globals(), locals(), [], 1)
                    func = getattr(digos_import, digo)
                    returnNecessaryInputSettings = func.returnNecessaryInputSettings()
                    Typelist = returnNecessaryInputSettings['type']
                    Api = returnNecessaryInputSettings['need_api']
                    Username = returnNecessaryInputSettings['need_username']
                    Password = returnNecessaryInputSettings['need_password']
                    if type(Typelist) == list:
                        for Type in Typelist:
                            if Type not in settings:
                                settings[Type] = {}
                            settings[Type][digo] = {'ison':'OFF', 'need_api': Api, 'need_username': Username, 'need_password': Password}
        return settings




    def set_settings(self, settings):
        query = 'MATCH (n) WHERE n.username="'+self.username+'" SET n.settings="'+str(settings)+'"'
        n = gdb.query(query)
        return True










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
