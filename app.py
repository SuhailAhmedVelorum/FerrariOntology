from flask import Flask, render_template, request
import requests
from backend import *
import pprint
pp = pprint.PrettyPrinter(indent=4)


app = Flask(__name__)


def makeReadable(camel: str):
    count = 0
    words = []
    prevBreak = 0
    for i in range(len(camel)):
        letter = camel[i]
        if letter.isupper():
            words.append(camel[prevBreak:count])
            prevBreak = count
        if i == len(camel) - 1:
            words.append(camel[prevBreak:count + 1])
        count += 1
    newWord = ""
    for word in words:
        if word == "":
            continue
        newWord += word[0].upper() + word[1:] + " "
    newWord = newWord.strip()
    return newWord


def sortNamingIssues(model: str):
    if "ferrari" in model.lower():
        return model.upper()
    else:
        return "FERRARI " + model.upper()


def initialize():
    modelDetails = fetchRandomModel()
    trivia = modelDetails['trivia']
    model = modelDetails['model']
    if 'trivia' in modelDetails:
        del modelDetails['trivia']
    if 'model' in modelDetails:
        del modelDetails['model']
    toServe = dict()
    model = sortNamingIssues(model)
    for key in modelDetails.keys():
        toServe[makeReadable(key)] = modelDetails[key]
    return toServe, trivia, model


@app.route('/')
def index():
    modelDetails, trivia, model = initialize()
    return render_template('index.html', model=model, trivia=trivia, modelDetails=modelDetails)


if __name__ == "__main__":
    app.run()
