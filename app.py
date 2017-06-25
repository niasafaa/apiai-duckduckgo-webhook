#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request


import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "DuckDuckGoInstantAnswer":
        return {}
    baseurl = "http://api.duckduckgo.com/?"
    yql_query = makeYqlQuery(req)
    print ("YQL_QUERY\n" + yql_query)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    print("yql_url:" + yql_url)
    result = urlopen(yql_url).read().decode("utf8")
    print (result)
    data = json.loads(result)
    print (data)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    query = result.get("resolvedQuery")
    if query is None:
        return None

    return query


def makeWebhookResult(data):
    answer = data.get('Abstract')
    if answer is None:
        return {}

    print(json.dumps(answer, indent=4))

    speech = answer

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-duckduckgo-webhook"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
