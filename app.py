from flask import Flask, request
import requests, json, os
from api import covid_update

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
URL = f"https://graph.facebook.com/v6.0/me/messages?access_token={ACCESS_TOKEN}"
headers = {
        'Content-Type': 'application/json'
    }

@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        print("something")
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return 'Invalid verification token'

    else:
        #Get the json representation of the request
        body = request.get_json()
        # print(body)
        if body.get('object') == "page":
            for event in body['entry']:
                webhook_event = event['messaging'][0]
                sender_psid = webhook_event['sender']['id']
                print(webhook_event)
                set_sender_status(sender_psid=sender_psid,action='mark_seen')
                # Get user info from sender_psid
                res = requests.get(f"https://graph.facebook.com/{sender_psid}?fields=first_name,last_name,profile_pic&access_token={ACCESS_TOKEN}")
                profile_info = res.json()
                print(profile_info)

                if 'message' in webhook_event:
                    set_sender_status(sender_psid=sender_psid,action='typing_on')
                    handle_message(sender_psid, webhook_event['message'],profile_info=profile_info)
                elif 'postback' in webhook_event:
                    set_sender_status(sender_psid=sender_psid,action='typing_on')
                    handle_postback(sender_psid, webhook_event['postback'])


            return 'event received'
        else:
            return '404 not found'
        # pprint.pprint(output)
        # print(len(output['entry']))
        # for event in output['entry']:
        #     messaging = event['messaging']

        return "Message Processed"


def handle_message(sender_psid, received_message, profile_info):
    response = {}
    if 'text' in received_message:
        
        if 'nlp' in received_message:
            nlp = received_message['nlp']
            if 'entities' in nlp:
                entities = nlp['entities']
                if 'greetings' in entities:
                    if entities['greetings'][0]['confidence'] > 0.7:
                        response = {
                            "text": f"{received_message['text']} {profile_info['first_name']}. Try one of the options in the menu."
                        }
                    else:
                        response = {
                            "text": f"Hello {profile_info['first_name']}. Try one of the options in the menu."
                        }
                else:
                    response = {
                        "text": f"Sorry I can't understand what you're saying! Try one of the options in the menu."
                    }
        print(response)

    elif 'attachments' in received_message:
        attachment_url = received_message['attachments'][0]['payload']['url']
        response = {
            "attachment": {
                "type": "template",
                "payload": {
                "template_type": "generic",
                "elements": [{
                    "title": "Is this the right picture?",
                    "subtitle": "Tap a button to answer.",
                    "image_url": attachment_url,
                    "buttons": [
                    {
                        "type": "postback",
                        "title": "Yes!",
                        "payload": "yes",
                    },
                    {
                        "type": "postback",
                        "title": "No!",
                        "payload": "no",
                    }
                    ],
                }]
                }
            }
        }
    call_send_api(sender_psid, response)

def handle_postback(sender_psid, received_message):
    # print(received_message)
    payload = received_message['payload']

    # If get started is called
    if(payload == "greeting"):
        response = { "text": "No greeting!" }
    if(payload == 'yes'):
        response = { "text": "Thanks!" }
    elif(payload == 'no'):
        response = { "text": "Oops, try sending another image." }
    elif(payload == 'about_covid_19'):
        response = {
            "attachment":{
            "type":"template",
            "payload":{
                "template_type":"button",
                "text": "Covid-19 is an infectious disease caused by a new coronavirus.\nThe disease causes respiratory illness (like the flu) with symptoms such as a cough, fever, and in more severe cases, difficulty breathing.\n You can protect yourself by washing your hands frequently, avoiding touching your face, and avoiding close contact (1 meter or 3 feet) with people who are unwell.",
                "buttons":[
                    {
                        "type":"web_url",
                        "url":"https://www.who.int/emergencies/diseases/novel-coronavirus-2019",
                        "title":"View WHO Website"
                    },             
                    ]      
                }
            }
        }
    elif(payload == 'symptoms'):
        response = {
            "attachment":{
                "type":"image", 
                "payload":{
                    "url":"https://www.uab.edu/news/images/2018/Coronavirus-Symptoms-graphic.jpg", 
                    "is_reusable":True
                }
            }
        }
    elif(payload == 'preventive_measures'):

        response = {
            "attachment":{
                "type":"image", 
                "payload":{
                    "url":"https://i.ibb.co/N7DTQHs/coronaprevention.png", 
                    "is_reusable":True
                }
            }
        }
    elif(payload == 'compare_symptoms_with_flu'):
        response = {
            "attachment":{
                "type":"image", 
                "payload":{
                    "url":"https://cgsentinel.com/uploads/images/2020/03/825185e2f83c3dc648d7efbeb725bc6c.jpg", 
                    "is_reusable":True
                }
            }
        }
        call_send_api(sender_psid, response)
        set_sender_status(sender_psid,'typing_on')
        response = {
            "attachment":{
                "type":"image", 
                "payload":{
                    "url":"https://www.verywellhealth.com/thmb/dUqyKHHvwh_dTOG0ijezERNQF04=/1500x1000/filters:no_upscale():max_bytes(150000):strip_icc()/coronavirus-flu-differences-4798752-v1-46194f3009ac4f3d80b4078fd180bbb7.png", 
                    "is_reusable":True
                }
            }
        }
    elif(payload == 'compare_stat_with_flu'):
        response = {
            "attachment":{
                "type":"image", 
                "payload":{
                    "url":"https://cdn.vox-cdn.com/thumbor/ZjHuZAFwRiWB72rdUO4qTKJCnis=/0x0:1941x1941/1200x0/filters:focal(0x0:1941x1941):no_upscale()/cdn.vox-cdn.com/uploads/chorus_asset/file/19816388/flu_covid_comparison_1_high_res.jpg", 
                    "is_reusable":True
                }
            }
        }
        call_send_api(sender_psid, response)
        set_sender_status(sender_psid,'typing_on')
        response = {
            "attachment":{
                "type":"image", 
                "payload":{
                    "url":"https://img.apmcdn.org/e565a7c003ccf26b6ffbffc18b4964f04f8e0f0d/uncropped/2bc5fb-20200311-coronavirus-charts02.png", 
                    "is_reusable":True
                }
            }
        }
    elif(payload == "total_global_cases"):
        response = {
            "text" : covid_update('all')
        }
    elif(payload == "total_nepal_cases"):
        response = {
            "text" : covid_update('nepal')
        }
    
    
        
    call_send_api(sender_psid, response)

def call_send_api(sender_psid, response):
    request_body = {
        "recipient": {
         "id": sender_psid
        },
        "message": response
    }
    get_response = requests.post(URL,headers=headers,data=json.dumps(request_body) )
    set_sender_status(sender_psid=sender_psid,action='typing_off')

def set_sender_status(sender_psid,action):
    data = {
        "recipient":{
            "id":sender_psid
        },
        "sender_action": action
    }
    response = requests.post(URL,headers=headers,data=json.dumps(data))


if __name__ == "__main__":
    app.run('localhost',5000)
        

