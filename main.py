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
import emoji
import pickle
from functools import reduce
import sklearn
from sklearn.feature_extraction.text import CountVectorizer

pickle_in = open('hatecrimemodel.pickle', 'rb')
pickle_in2 = open('cv.pickle', 'rb')
pickle_clf = pickle.load(pickle_in)
pickle_cv = pickle.load(pickle_in2)
stemmer = nltk.SnowballStemmer("english")
stopword=set(stopwords.words('english'))

app = Flask(__name__)
def cleanOnly(tex):
        tex = str(tex).lower()
        tex = re.sub('\[.*?\]', '', tex)
        tex = re.sub('https?://\S+|www\.\S+', '', tex)
        tex = re.sub('<.*?>+', '', tex)
        tex = re.sub('[%s]' % re.escape(string.punctuation), '', tex)
        tex = re.sub('\n', '', tex)
        tex = re.sub('\w*\d\w*', '', tex)
        tex = re.sub("[^a-zA-Z0-9 ]+", '',tex)
        tex = ''.join(c for c in tex if c not in emoji.UNICODE_EMOJI) #Remove Emojis
        tex = [word for word in tex.split(' ') if word not in stopword]
        tex=" ".join(tex)
        tex = [stemmer.stem(word) for word in tex.split(' ')]
        tex=" ".join(tex)
        return tex

def getSentiment(text):
    def clean(tex):
        tex = str(text).lower()
        tex = re.sub('\[.*?\]', '', tex)
        tex = re.sub('https?://\S+|www\.\S+', '', tex)
        tex = re.sub('<.*?>+', '', tex)
        tex = re.sub('[%s]' % re.escape(string.punctuation), '', tex)
        tex = re.sub('\n', '', tex)
        tex = re.sub('\w*\d\w*', '', tex)
        tex = re.sub("[^a-zA-Z0-9 ]+", '',tex)
        tex = ''.join(c for c in tex if c not in emoji.UNICODE_EMOJI) #Remove Emojis
        tex = [word for word in tex.split(' ') if word not in stopword]
        tex=" ".join(tex)
        tex = [stemmer.stem(word) for word in tex.split(' ')]
        tex=" ".join(tex)
        return tex
    return text, TextBlob(clean(text)).sentiment.polarity

def AveragePolarity(tweets):
    if tweets != -1:
        tweets = (dict(json.loads(tweets))['content']).values()
        tweetNsentiment = list(map(getSentiment, tweets))
        return sum(map(lambda x: x[1], tweetNsentiment))/len(tweets), tweetNsentiment
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
    du = AveragePolarity(d)
    sh = AveragePolarity(s)
    fu = AveragePolarity(f)
    uq = AveragePolarity(u)
    az = AveragePolarity(ad)
    ajj = AveragePolarity(aj)
    rk = AveragePolarity(r)
    arr = []
    if type(du) != int:
        arr.append(list(du[1]))
    else:
        du = [0]
    if type(sh) != int:
        arr.append(list(sh[1]))
    else:
        sh = [0]
    if type(fu) != int:
        arr.append(list(fu[1]))
    else:
        fu = [0]
    if type(uq) != int:
        arr.append(list(uq[1]))
    else:
        uq = [0]
    if type(az) != int:
        arr.append(list(az[1]))
    else:
        az = [0]
    if type(ajj) != int:
        arr.append(list(ajj[1]))
    else:
        ajj = [0]
    if type(rk) != int:
        arr.append(list(rk[1]))
    else:
        rk = [0]
    arr = reduce(lambda x, y: x+y, arr)

    pos = list(filter(lambda pred: pred[1]>0, arr))
    neg = list(filter(lambda pred: pred[1]<0, arr))
    neut = list(filter(lambda pred: pred[1]==0, arr))
    hateCrime = [ (sample[0], pickle_clf.predict(pickle_cv.transform([cleanOnly(sample[0])]).toarray())[0]) for sample in neg ]
    #print(hateCrime)
    



    a = jsonify(
        
            {
                'plot':{'ae-du' : du[0], 'ae-sh' : sh[0], 'ae-fu' : fu[0], 'ae-uq' : uq[0], 'ae-az' : az[0], 'ae-aj' : ajj[0], 'ae-rk' : rk[0], 'ae-740':0, 'ae-742':0},
                'pos': pos,
                'neg': neg,
                'neut': neut,
                'hate': hateCrime
            }

    )
    #print(a)
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
        int(items = request.args.get('items', 10, type=int))
    df = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
    f'{keyword} lang:en near:"Ajman" within:10km').get_items(), items))[['date', 'content']]
    return df.to_json()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)