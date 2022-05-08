from flask import Flask, request, url_for, redirect, render_template, jsonify
import pandas as pd
import itertools
import snscrape.modules.twitter as sntwitter
from textblob import TextBlob
import re
import nltk
from nltk.corpus import stopwords
import string
import json
import asyncio

stemmer = nltk.SnowballStemmer("english")
stopword=set(stopwords.words('english'))

app = Flask(__name__)

def getSentiment(text):
    def clean(text):
        text = str(text).lower()
        text = re.sub('\[.*?\]', '', text)
        text = re.sub('https?://\S+|www\.\S+', '', text)
        text = re.sub('<.*?>+', '', text)
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub('\n', '', text)
        text = re.sub('\w*\d\w*', '', text)
        text = [word for word in text.split(' ') if word not in stopword]
        text=" ".join(text)
        text = [stemmer.stem(word) for word in text.split(' ')]
        text=" ".join(text)
        return text
    return TextBlob(clean(text)).sentiment.polarity

def AveragePolarity(tweets):
    if tweets != -1:
        tweets = (dict(json.loads(tweets))['content']).values()
        return sum(map(getSentiment, tweets))/len(tweets)
    else:
        return 0


@app.route('/allpolarity')
async def polarities():
    keyword = request.args.get('keyword', "EidMubarak", type=str)
    items = request.args.get('items', 10, type=int)
    d,s,f,u,ad,aj,r = await dubai(keyword, items), await sharjah(keyword, items), await fujairah(keyword, items), await UmmAlQuywain(keyword, items), await abudhabi(keyword, items), await ajman(keyword, items), await rak(keyword, items)
    print(d,s,f,u,ad,aj,r)
    # a = jsonify(
    #     {'polarities':
    #         {'ae-du' : AveragePolarity(d), 'ae-sh' : AveragePolarity(s), 'ae-fu' : AveragePolarity(f), 'ae-uq' : AveragePolarity(u), 'ae-az' : AveragePolarity(ad), 'ae-aj' : AveragePolarity(aj), 'ae-rk' : AveragePolarity(r), 'ae-740':0, 'ae-742':0}
    #     },'tweets': 
    #         {idx: (tweet, polarity) for }

    # )
    a = jsonify(
        
            {'ae-du' : AveragePolarity(d), 'ae-sh' : AveragePolarity(s), 'ae-fu' : AveragePolarity(f), 'ae-uq' : AveragePolarity(u), 'ae-az' : AveragePolarity(ad), 'ae-aj' : AveragePolarity(aj), 'ae-rk' : AveragePolarity(r), 'ae-740':0, 'ae-742':0}
       

    )
    print(a)
    return a


@app.route('/dubai/', methods=['GET', 'POST'])
async def dubai(keyword=None, items=None):
    if not keyword:
        keyword = request.args.get('keyword', "eid", type=str)
    if not items:
        items = request.args.get('items', 10, type=int)
    df = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
    f'{keyword} lang:en near:"Dubai" within:10km').get_items(), items))[['date', 'content']]
    return df.to_json()

@app.route('/sharjah/', methods=['GET', 'POST'])
async def sharjah(keyword=None, items=None):
    if not keyword:
        keyword = request.args.get('keyword', "eid", type=str)
    if not items:
        items = request.args.get('items', 10, type=int)
    df = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
    f'{keyword} lang:en near:"Sharjah" within:10km').get_items(), items))[['date', 'content']]
    return df.to_json()

@app.route('/fujairah/', methods=['GET', 'POST'])
async def fujairah(keyword=None, items=None):
    if not keyword:
        keyword = request.args.get('keyword', "eid", type=str)
    if not items:
        items = request.args.get('items', 10, type=int)
    try:
        df = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
        f'{keyword} lang:en near:"Fujairah" within:10km').get_items(), items))[['date', 'content']]
        return df.to_json()
    except:
        return -1

@app.route('/umm/', methods=['GET', 'POST'])
async def UmmAlQuywain(keyword=None, items=None):
    keyword = request.args.get('keyword', "eid", type=str)
    items = request.args.get('items', 10, type=int)
    df = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
    f'{keyword} lang:en near:"Umm Al Quywain" within:10km').get_items(), items))[['date', 'content']]
    return df.to_json()

@app.route('/abudhabi/', methods=['GET', 'POST'])
async def abudhabi(keyword=None, items=None):
    if not keyword:
        keyword = request.args.get('keyword', "eid", type=str)
    if not items:
        items = request.args.get('items', 10, type=int)
    df = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
    f'{keyword} lang:en near:"Abu Dhabi" within:10km').get_items(), items))[['date', 'content']]
    return df.to_json()

@app.route('/rak/', methods=['GET', 'POST'])
async def rak(keyword=None, items=None):
    if not keyword:
        keyword = request.args.get('keyword', "eid", type=str)
    if not items:
        items = request.args.get('items', 10, type=int)
    try:
        df = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
        f'{keyword} lang:en near:"Ras Al Khaima" within:10km').get_items(), items))[['date', 'content']]
        return df.to_json()
    except:
        return -1

@app.route('/ajman/', methods=['GET', 'POST'])
async def ajman(keyword=None, items=None):
    if not keyword:
        keyword = request.args.get('keyword', "eid", type=str)
    if not items:
        items = request.args.get('items', 10, type=int)
    df = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
    f'{keyword} lang:en near:"Ajman" within:10km').get_items(), items))[['date', 'content']]
    return df.to_json()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)