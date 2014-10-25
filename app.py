from flask import Flask, request, redirect
import twilio.twiml
 
app = Flask(__name__)
 
@app.route("/twilio_sms", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""
 
    body = request.values.get('Body')

    resp = twilio.twiml.Response()
    resp.message("Hello, " + body)
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)