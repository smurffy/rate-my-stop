from flask import Flask, request, redirect, session
import os
import config
import twilio.twiml
 
app = Flask(__name__)

app_config = os.environ.get('APP_SETTINGS', 'config.DevelopmentConfig')
app.config.from_object(app_config)
 
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

        # TODO: save data here

        del session['stop_id']
        resp = twilio.twiml.Response()
        resp.message("Thanks for your feedback!")
        return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)