from flask import Flask, render_template, request
from.models import DB, User, Tweet
from .twitter import add_or_update_user
import pickle
from .logreg import score_calc
from sklearn.datasets import load_iris
from .predict import predict_user

def create_app():

    app = Flask(__name__)

    #database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # register our database with the app
    DB.init_app(app)
    
    
    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)
    
    @app.route('/reset')
    def reset():
        #drop all database tables
        DB.drop_all()
        #recreate all database tables according to indicated schema in models
        DB.create_all()
        return render_template('base.html', title='Reset')

    @app.route('/populate')
    def populate():
        add_or_update_user('NASA')
        add_or_update_user('elonmusk')
        add_or_update_user('Austen')
        
        return render_template('base.html', title='Populated')
    
    @app.route('/update')
    def update():
        #get list of all usernames
        users = User.query.all()
        #usernames = []
        #for user in users:
        #   usernames.append(user.username)

        #[user.username for user in users]
        for username in [user.username for user in users]:
            add_or_update_user(username)
        
        return render_template('base.html', title='Updated')
    
    @app.route('/iris')
    def iris():    
        
        X, y = load_iris(return_X_y=True)
        clf_pickled = score_calc()
        clf_unpickled = pickle.loads(clf_pickled)

        return str(clf_unpickled.predict(X[:2, :]))
    
    @app.route('/score')
    def score():    
        X, y = load_iris(return_X_y=True)
        clf_pickled = score_calc()
        clf_unpickled = pickle.loads(clf_pickled)
        return str(clf_unpickled.score(X, y))
    
    @app.route('/user', methods = ['POST'])
    @app.route('/user/<username>', methods = ['GET'])
    def user(username=None, message=''):

        username = username or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = f'User {username} has been successfully added.'

            tweets = User.query.filter(User.username==username).one().tweets
        except Exception as e:
            message = f'Error adding {username}: {e}.'
            tweets = []
            
            
        return render_template('user.html', title=username, tweets=tweets, message=message)
            

    @app.route('/compare', methods = ['POST'])
    def compare():
        
        user0, user1 = sorted([request.values['user0'], request.values['user1']])
        hypo_tweet_text = request.values['tweet_text']

        if user0 == user1:
            message = 'Cannot compare user to themselves.'
        else:
            prediction = predict_user(user0, user1, hypo_tweet_text)

            if prediction: # get into this block if prediction is 1 (user1)
                message = f'This tweet is likely to have been tweeted by {user1}'
            else:
                message = f'This tweet is likely to have been tweeted by {user0}'

        return render_template('prediction.html', title = 'Prediction', message=message)



    return app
       