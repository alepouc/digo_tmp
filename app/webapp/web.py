#!/usr/bin/env python

from datetime import datetime
from flask import Flask, request, jsonify, render_template, Response
from neo4jrestclient.client import GraphDatabase
import time
import json
from pprint import pprint


#time.sleep(7)
app = Flask(__name__)

gdb = GraphDatabase("http://digo-db:7474/db/data", username="neo4j", password="debug")


@app.route('/')
def index():
    return render_template('graph.html')


@app.route("/graph")
def get_graph():
    #query = 'MATCH p=shortestPath( (bacon:Person {name:"Kevin Bacon"})-[*]-(meg:Person {name:"Meg Ryan"}) ) RETURN p'
    #query = 'MATCH (people:Person)-[relatedTo]-(:Movie {title: "Cloud Atlas"}) RETURN people.name, Type(relatedTo), relatedTo'
    #query = 'MATCH (n) RETURN n'
    query = 'MATCH (n)-[r]-(m) RETURN n, r, m limit 3'

    results = gdb.query(query, data_contents=True)

    nodes = ""
    edges = ""

    for row in results.graph:
        #pprint(results.graph)
        if str(row['relationships']) != "[]":
            edges += str(row['relationships']).split("[", 1)[1].rsplit("]", 1)[0]+","
        nodes += str(row['nodes']).split("[", 1)[1].rsplit("]", 1)[0]+","


    nodes = '{"nodes":['+nodes.replace("{'",'{"').replace(" '",' "').replace("'}",'"}').replace("' ",'" ').replace("['",'["').replace("']",'"]').replace("',",'",').replace("':",'":').rsplit(",", 1)[0]+']}'
    edges = '{"edges":['+edges.replace("{'",'{"').replace(" '",' "').replace("'}",'"}').replace("' ",'" ').replace("['",'["').replace("']",'"]').replace("',",'",').replace("':",'":').rsplit(",", 1)[0]+']}'


    json_list_nodes = json.loads(nodes)
    json_list_edges = json.loads(edges)


    new_list_nodes = []
    for item in json_list_nodes['nodes']:
        if item not in new_list_nodes:
            new_list_nodes.append(item)


    new_list_edges = []
    for item in json_list_edges['edges']:
        if item not in new_list_edges:
            new_list_edges.append(item)

    #print(new_list_edges)

    new_result = '{"nodes":['+str(json.dumps(new_list_nodes))+'],"edges":['+str(json.dumps(new_list_edges))+']}'
    new_result = new_result.replace('[[','[').replace(']]',']')
    new_result = new_result.replace('},]','}]').replace('startNode', 'source').replace('endNode', 'target')


    return new_result



app.run(host='0.0.0.0', port=5000, debug = True)
