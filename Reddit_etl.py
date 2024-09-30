import requests
import requests.auth
import pandas as pd
from textblob import TextBlob

def reddit_Extraction():
    CLIENT_ID = '2v7MESwQm_3Xu1hkYygkSQ'
    SECRET_KEY=	'a5dMZ27skiv8qd0aclw0HAuovHnBFA'
    USERNAME =  'Chinmayi_Prakash'
    PASSWORD = 'Chinthan031*'
    #Authentication Instance
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID,SECRET_KEY)
    #creating a dictionary containing authentication details
    data = {
        'grant_type':'password',
        'username': USERNAME,
        'password':PASSWORD
    }

    headers = {'User-Agent':'MyAPI/0.0.1'}

    url = 'https://www.reddit.com/api/v1/access_token'

    res = requests.post(url,auth=auth,data=data,headers=headers)

    TOKEN = res.json()['access_token']

    headers['Authorization'] = f'bearer {TOKEN}'

    #print(headers)
    request_url = 'https://oauth.reddit.com/r/Ask_Politics/hot'
    res = requests.get(request_url,headers=headers)

    print(res.json)

    posts = []
    for post in res.json()['data']['children']:
        selftext = post['data']['selftext']
        sentiment = TextBlob(selftext).sentiment.polarity
        sentiment_label = 'positive' if sentiment > 0 else 'negative' if sentiment < 0 else 'neutral'
        
        posts.append({
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'sentiment': sentiment_label,  # Adding sentiment label
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score']
        })
    df = pd.DataFrame(posts)
    df.to_csv('s3://reddit-etl-chinmayi/reddit.csv')

    print(df)