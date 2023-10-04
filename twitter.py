from os import getenv
import not_tweepy as tweepy
from .models import DB, Tweet, User
import spacy

# get our API keys from .env file 
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

# connect to the twitter API
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
TWITTER = tweepy.API(TWITTER_AUTH)

def add_or_update_user(username):
    ''' take username and pull user data and tweets from API. If already 
    present in Database, check for news and add to DB'''
    try:
        # get user information
        twitter_user = TWITTER.get_user(screen_name=username)

        # check to see if user is already in database 
        # if user not present, create one
        db_user = (User.query.get(twitter_user.id)) or User(id=twitter_user.id, username=username)

        #add the user to the database, will only execute if not already present
        DB.session.add(db_user)

        # get users tweets in a list
        tweets = twitter_user.timeline(count=200, exclude_replies=True,
                                    include_rts=False, tweet_mode='extended',
                                    since_id=db_user.newest_tweet_id)
        
        if tweets:
            db_user.newest_tweet_id= tweets[0].id
        
        #add all of the tweets indiviually to database
        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id, 
                            text=tweet.full_text[:300], 
                            vect=tweet_vector,
                            user_id=db_user.id)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print(f'Error processing {username}: {e}')
        raise e 
    
    else:
        #save the changes to the database
        DB.session.commit()

nlp = spacy.load('my_model/')
# function turns text into vectors of word embedding
def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector
