#!/usr/bin/env python

from datetime import datetime
from flask import Flask, request, jsonify, render_template, Response
from neo4jrestclient.client import GraphDatabase
import time
import json
from pprint import pprint
import random


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
    query = 'MATCH (n)-[r]-(m) RETURN n, r, m limit 5'
    results = gdb.query(query, data_contents=True)
    SigmaJSON = convertNeo4jJsonToSigma(results.graph)
    return SigmaJSON




@app.route('/transform_table')
def get_transform_table():
    transform_table = {
                        "Person":["actionPerson_A", "actionPerson_B"],
                        "Movie":["actionMovie_C", "actionMovie_D"],
                      }
    return jsonify(transform_table)





@app.route('/action')
def get_actions():
    time.sleep(2)
    return '{"actions":["action1", "action2"]}'



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug = True)
