from flask import Flask, request, redirect, session, Response
from flask.ext.sqlalchemy import SQLAlchemy
import os
import datetime
from pytz import timezone, utc
import twilio.twiml
import json
 
import config

app = Flask(__name__)
db = SQLAlchemy(app)

app_config = os.environ.get('APP_SETTINGS', 'config.DevelopmentConfig')
app.config.from_object(app_config)

class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.String(10), db.ForeignKey('stop.stop_id'))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone = True))
    sentiment = db.Column(db.Text)
    stop = db.relationship('Stop')

class Stop(db.Model):
    stop_id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(80))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

db.create_all()

def sentiment_analysis(feedback):
    condition = "text"+"="+feedback
    url = 'http://text-processing.com/api/sentiment/'
    r = requests.post(url, data=condition)
    #print sentiment_response.json()
    json_response = r.json()

    def sentiment_value(sentiment_response):
        feedback_sentiment = json_response['label']
        #print feedback_sentiment
        return feedback_sentiment

    sentiment_value(json_response)

@app.route("/twilio_sms", methods=['GET', 'POST'])
def incoming_sms():
    """Respond to incoming calls with a simple text message."""
    
    if 'stop_id' not in session:
        # if it's the first text...

        # TODO: validate that the stop_id is a stop id
        session['stop_id'] = request.values.get('Body')

        resp = twilio.twiml.Response()
        resp.message("Tell us your feedback:")
        return str(resp)
    else: 
        # if it's the 2nd text...

        feedback = request.values.get('Body')

        # TODO: do sentiment analysis
        sentiment = sentiment_analysis(feedback)

        save_data(session['stop_id'], feedback, sentiment)

        del session['stop_id']
        db.session.commit()
        # TODO: check that this doesn't leave you in a loop if you pass an invalid stop id

        resp = twilio.twiml.Response()
        resp.message("Thanks for your feedback!")
        return str(resp)
 
# how do i...
# fetch all feedback, map them into json, group by stop_id...?

# From http://stackoverflow.com/questions/6999726/python-converting-datetime-to-millis-since-epoch-unix-time
def unix_time(dt):
    epoch = datetime.datetime(1970, 1, 1, tzinfo=utc)
    delta = dt - epoch
    return delta.total_seconds()


@app.route('/')
def query_all_data():
    all_feedbacks = Feedback.query.all()

    stops = set([feedback.stop for feedback in all_feedbacks])

    result = [{
        'stop_id': stop.stop_id,
        'lat': stop.latitude,
        'long': stop.longitude,
        'feedback': [{
            'datetime': int(unix_time(feedback.created_at)),
            'comment': feedback.comment,
            'sentiment': 'pro' # replace me with working code
        } for feedback in all_feedbacks if feedback.stop_id == stop.stop_id]
    } for stop in stops]

    

    return Response(json.dumps(result), mimetype='application/json')

def save_data(stop_id, comment, sentiment):
    pacific = timezone('US/Pacific')

    feedback = Feedback(stop_id=stop_id,
                        comment=comment,
                        sentiment =sentiment,
                        created_at=datetime.datetime.now(pacific))
    db.session.add(feedback)

if __name__ == "__main__":
    app.run(debug=True)