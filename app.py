from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response
from lxml import html
from io import StringIO, BytesIO
import requests

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    #print("Request:")
    #print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    result = req.get("result")
    parameters = result.get("parameters")
    protein = parameters.get("protein")
    vegetable = parameters.get("vegetable")
    dishtype = parameters.get("dish-type")

    url = "http://panlasangpinoy.com/?s=" + protein + "+" + vegetable + "+" + dishtype + "&sort=re"

    print(url)
    speech = parseHtml(url)

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "CRAB"
    }

def parseHtml(url):
    listDish = "You may try the following:\r\n"
    page = requests.get(url)
    tree = html.fromstring(page.content)
    searchContainer = tree.xpath("//body/div[@class='site-container']/div[@class='site-inner']/div[@class='content-sidebar-wrap']/main[@class='content']/article")
    
    for article in searchContainer:
        dish = article.xpath("header[@class='entry-header']/h2[@class='entry-title']/a")
        listDish += dish[0].text.strip() + "\r\n"

    if listDish.strip() == "You may try the following:":
        listDish = "Cannot find any recipe\r\n"

    return listDish

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
