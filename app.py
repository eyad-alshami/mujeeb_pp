# -*- coding:utf-8 -*-
import os
import sys
import string
import requests
import json
import re
import systran_translation_api
from flask import Flask, request
import os.path

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai


app = Flask(__name__)

CLIENT_ACCESS_TOKEN = '7be6ca066fee47e4859143db14d1ae1a'

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
    #log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the 
                    
                    result = translate(message_text, target="en")
                    log(result)

                    if result:
                        action, response_message = get_response(result, session=sender_id)
                        if action == u'input.unknown':
                            result = translate(response_message, target="ar")
                        else:
                    	   send_message(sender_id, translate(response_message ,target="ar"))
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
        #log(r.status_code)
        #log(r.text)

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

def translate(text, target): 

    '''
    text: text to translate
    source: language code (en, ar) or empty string ''
    target: language code
    '''

    cookies = {
        'ARRAffinity': '381886f20a3d4c650efb6ba6743a59f751cd73ed32db817570e593f55e05a0e6',
        'dnn.lang_to': 'ar',
    }

    headers = {
        'Origin': 'https://translator.microsoft.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/53.0.2785.143 Chrome/53.0.2785.143 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://translator.microsoft.com/neural',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }

    data = {
        "Text": text,
        "SourceLanguage": "ar",
        "TargetLanguage": target
    }

    r = requests.post('https://translator.microsoft.com/neural/api/translator/translate', headers=headers, cookies=cookies, data=json.dumps(data))
    try:
        jobject = json.loads(r.text)
        return jobject['resultNMT']        
    except Exception:
        log("error in MICROSOFT JSON file")
        log(r.text)
        return u"يوجد خطأ في الترجمة"

    

def get_response(query, session="000"):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()

    request.lang = 'en'  # optional, default value equal 'en'

    request.session_id = session

    request.query = query

    response = request.getresponse()
    try:
        jobject = json.loads(response.read().decode('utf-8'))
    except Exception:
        log("error in API JSON file")

    return jobject["result"]['action'], jobject["result"]["fulfillment"]["speech"]

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)
