from neo4j import GraphDatabase
from flask import Flask, render_template, request
import pandas as pd
import requests
import math
import random
import os
from creds import code, password

import pprint
pp = pprint.PrettyPrinter(indent=4)

WRITE = True


def debug(argument: str, clearOnNew: bool = True):
    if WRITE:
        if os.path.exists("quiz.txt"):
            if(clearOnNew):
                with open('quiz.txt', 'w', encoding="utf-8") as debug:
                    debug.truncate(0)
                    debug.write(str(argument))
            else:
                with open('quiz.txt', 'a', encoding="utf-8") as debug:
                    debug.write(str(argument))
            debug.close()


uri = "neo4j+s://" + code + ".databases.neo4j.io"
driver = GraphDatabase.driver(uri, auth=(
    "neo4j", password))


def queryCount(tx):
    result = tx.run("MATCH(j: History) RETURN count(j)")
    for record in result:
        return record[0]


def queryNMatch(tx, model):
    modelDetails = []
    result = tx.run("MATCH(j: History {model: '" + model+"'}) RETURN j")
    for record in result:
        modelDetails.append(record[0])
    return modelDetails


def findModelAtIndex(tx, index):
    result = tx.run("MATCH(j: History) RETURN j")
    iter = 0
    for record in result:
        if(iter == index):
            return record[0]
        iter += 1
    else:
        return None


modelDetails = {}


def fetchRandomModel():
    with driver.session() as session:
        randomNumber = int(math.floor(
            random.uniform(0, 1) * queryCount(session)))
        modelName = findModelAtIndex(session, randomNumber)
        model = modelName['model']
        fetchedModel = queryNMatch(session, model)[0]
        for spec in fetchedModel:
            modelDetails[spec] = fetchedModel[spec]
        driver.close()
    return modelDetails
