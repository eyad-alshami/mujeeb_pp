# -*- coding:utf-8 -*-
import os
import sys
import string
import requests
import json
import re
import systran_translation_api
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    initialize_tra()
    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the 
                    
                    result = translate(message_text,target="en")
                    if result:
                    	send_message(sender_id, result)
                    else:
                    	send_message(sender_id, message_text)


                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    #log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

# def translate(msg):
# 	api_key_file = r'api_key.txt'
# 	systran_translation_api.configuration.load_api_key(api_key_file)
# 	api_client = systran_translation_api.ApiClient()
# 	translation_api = systran_translation_api.TranslationApi(api_client)

# 	target = "en"
# 	if translation_api is not None:
# 		log("+++++++++++++++++++++++++")
# 		log(type(msg))
# 		log("+++++++++++++++++++++++++")
# 		result = translation_api.translation_text_translate_get( target = target, input = msg.encode("utf-8"))
# 		return result.outputs[0].output
# 	else:
# 		log("++++++++++++++++++++++")
# 		log("API is not valid")
# 		log("++++++++++++++++++++++")
# 		return None

def translate(text, source="ar", target="en"): # source & target are either ar, en or en, ar

    cookies = {
        'lang': 'en',
        'ses.sid': 's%3AYdbLoHsjRfk-jjm7PT-2PWg-5GH-NqDA.ygY0JWmQZqmoorUsKvKRwUTHGKttwDIMLaADn%2BjarYc',
    }

    headers = {
        'Host': 'demo-pnmt.systran.net',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-CSRF-Token': 'ZwbOllxv-0rcXInYO9RBpIdwPwFVlL1C0NP8',
        'x-user-agent': 'Translation Box',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://demo-pnmt.systran.net/production',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

    data = {
      'input': text,
      'source': source,
      'target': target,
      'owner': 'Systran',
      'domain': 'Generic',
      'size': 'M'
    }

    r = requests.post('https://demo-pnmt.systran.net/production/translate/html', headers=headers, cookies=cookies, data=data)
    j = json.loads(r.text)
    j = j['target'].split('\n')[2];
    j = re.split(r'\>|\<', j)
    return string.join(j[4::4], ' ')

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)
