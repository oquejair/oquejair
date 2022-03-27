import os
import tweepy

def login_twitter():
    ckey = os.environ["TW_CONSUMER_KEY"]
    cskey = os.environ["TW_CONSUMER_SECRET"]
    atoken = os.environ["TW_ACCESS_TOKEN"]
    astoken = os.environ["TW_ACCESS_TOKEN_SECRET"]

    api = tweepy.Client(
        consumer_key = ckey,
        consumer_secret = cskey,
        access_token = atoken,
        access_token_secret = astoken
    )

    return api

if __name__ == "__main__":
  login_twitter()
