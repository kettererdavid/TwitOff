from sklearn.linear_model import LogisticRegression
import numpy as np
from .models import User
from .twitter import vectorize_tweet

def predict_user(user0_username, user1_username, hypo_tweet_text):
    # grab users from database
    user0 = User.query.filter(User.username == user0_username).one()
    user1 = User.query.filter(User.username == user1_username).one()

    # get the word embeddings from each user
    user0_vects = np.array([tweet.vect for tweet in user0.tweets])
    user1_vects = np.array([tweet.vect for tweet in user1.tweets])

    # vertically stack the two numpy arrays to make the X_train
    X_train = np.vstack([user0_vects, user1_vects])

    # create labels 
    zeros = np.zeros(len(user0.tweets))
    ones = np.ones(len(user1.tweets))
    y_train = np.concatenate([zeros, ones])

    # vectorize hypo tweet text
    hypo_vect = vectorize_tweet(hypo_tweet_text).reshape(1,-1)
    
    # instantiate and fit logistic regression model 
    log_reg = LogisticRegression().fit(X_train, y_train)
   

    return log_reg.predict(hypo_vect)[0]

    

