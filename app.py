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

CLIENT_ACCESS_TOKEN = 'd78f2757db9d421eba31d03d08b03eae'

Api = {u'Ask.api': u"عذراً، لم أفهم ما قلته للتو."
    , u'Ask.name': u"اسمي مجيب، أستطيع مساعدتك لبناء عميل محادثة (chatbot) للإجابة على أسئلة عملائك."
    , u'Asking.present.tenses': u"أنا الآن أتحدث معك، أستطيع أيضاً بناء عميل محادثة خاص بك للإجابة على أسئلة عملائك"
    , u'Default Fallback Intent': u"آسف، لم أفهم ما قلته للتو."
    , u'Default Welcome Intent': u"مرحبا"
    , u'Mujeeb.about.team': u"صنعني فريق له خبرة في الذكاء الاصطناعي ومعالجة اللغات الطبيعية."
    ,
       u'Mujeeb.ai': u"يعتمد مجيب على الذكاء الاصطناعي بشكل أساسي، ولكن الطريق ما يزال طويلاً حتى الوصول لفهم آلي كامل للغة العربية"
    ,
       u'Mujeeb.build': u"يمكنك إرسال رابط صفحة الأسئلة الشائعة على موقعك أو ملف يحوي تلك الأسئلة ضمن هذه المحادثة. لمزيد من المعلومات، قم بزيارة mujeeb.ai"
    , u'Mujeeb.how.to.use': u"يمكنك تجربة مجيب عن طريق إدخال بياناتك هنا mujeeb.ai"
    , u'Mujeeb.services': u"يمكنني أن أبني عميل محادثة خاصاً بعملك أو خدمتك, يمكنك التسجيل في موقعي \n www.mujeeb.ai"
    ,
       u'Mujeeb.uses': u"انا عميل محادثة باللغة العربية او ما يسمى \n chatbot سيتمكن عملائك من استعمال خدمتك بشكل غير مسبوق، وسيمكنهم التحدث مع عميل المحادثة الخاص بك والتفاعل مع خدماتك دون انتظار وفي أي وقت."
    , u'Mujeeb.why.to.use.it': u"يوفر لك مجيب أحدث التقنيات وفريقاً خبيراً لتقديم واجهة محادثة تفاعلية وذكية لزبائنك."
    , u'user.love': u"وأنا أحبك أيضاً."
       }


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"][
                        "id"]  # the recipient's ID, which should be your page's facebook ID
                    try:
                        message_text = messaging_event["message"]["text"]  # the

                        result = translate(message_text, target="en")
                        log(result)
                        
                    except Exception:
                        send_message(sender_id, u"شكرا لك :)")

                    if result:
                        action, intent, response_message = get_response(result, session=sender_id)
                        log("++++++++++")

                        log(response_message)
                        log(action)
                        log(intent)
                        log("++++++++++")

                        try:
                            result = Api[intent]
                        except Exception:
                            log("no result")
                            result = response_message
                            send_message(sender_id, result)
                    else:
                        send_message(sender_id, u"أنا آسف لا يمكنني الرد على الرسائل حاليا، يتم إصلاحي وتطويري.")

                    

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):
    # log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

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
        log("")


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
        "SourceLanguage": "",
        "TargetLanguage": target,
    }

    r = requests.post('https://translator.microsoft.com/neural/api/translator/translate', headers=headers,
                      cookies=cookies, data=json.dumps(data))
    try:
        jobject = json.loads(r.text)
    except Exception:
        log("error in MICROSOFT JSON file")
        log(target)
        return u"اعذرني على قلة فهمي، يمكنك أن تستفسر عن : \n خدماتي \n الفريق المطور \n لماذا تريد ان تستخدمني \n تجريبي."

    return jobject['resultNMT']


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
        log("error in api JSON file")

    try:
        intent = jobject["result"]["metadata"]["intentName"]
        log(intent)
    except Exception:
        return jobject["result"]['action'], "no intent", "no response"

    return jobject["result"]["action"], intent, jobject["result"]['fulfillment'][
        'speech']  # jobject["result"]["metadata"]["intentName"]


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
