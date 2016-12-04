import systran_translation_api
import os
from flask import Flask, request
import json
import requests

initilized = False

if not initilized:

    api_key_file = r'api_key.txt'
    systran_translation_api.configuration.load_api_key(api_key_file)
    api_client = systran_translation_api.ApiClient()
    translation_api = systran_translation_api.TranslationApi(api_client)
    initilized = True
	
app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAAagtTCC7CQBAPAgrbNAJZCWybKZCRWIcJxpZC8pooXPFhMD2agqOZBriMAcJQbWSzTCizZAXyOonqBb1nAlyVFtcmqfZAehf6QYj0vaIJsBcx9EeILk9Wsb2BeHPtRX5vDN0wGTnzUjPLr6cW9yOmA39YmJvfJ4gh5NJyukJ1RAZDZD'

@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification."
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    print "Verification failed!"
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print "Handling Messages"
  payload = request.get_data()
  print payload
  for sender, message in messaging_events(payload):
    print "Incoming from %s: %s" % (sender, message)
    send_message(PAT, sender, message)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """
  
  if initilized:
        source = "ar"
        target = "en"
        input = [text]
        result = translation_api.translation_text_translate_get(source= source, target = target, input = input)
        txt= result.outputs[0].output
  else:
	txt = text
   
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": txt.encode('utf-8')}
#.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text


	

if __name__ == '__main__':
  app.run()