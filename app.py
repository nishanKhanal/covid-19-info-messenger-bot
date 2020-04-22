from flask import Flask, request
import requests, json, os, random
from api import covid_update, AFFECTED_COUNTRIES

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


                if 'message' in webhook_event:
                    set_sender_status(sender_psid=sender_psid,action='typing_on')
                    handle_message(sender_psid, webhook_event['message'],profile_info=profile_info)
                elif 'postback' in webhook_event:
                    set_sender_status(sender_psid=sender_psid,action='typing_on')
                    handle_postback(sender_psid, webhook_event['postback'],profile_info)


            return 'event received'
        else:
            return '404 not found'

        return "Message Processed"


def handle_message(sender_psid, received_message, profile_info):
    response = {}

    if 'quick_reply' in received_message:
        handle_postback(sender_psid, received_message['quick_reply'],profile_info)

    elif 'text' in received_message:
        if received_message['text'].lower() in AFFECTED_COUNTRIES:
            response = get_covid_update(received_message['text'].lower())

        elif received_message['text'].lower() in ['thanks','thanku','thank you','dhanyabd','tq','thank u']:
            welcome_texts = ['Welcome!', "You're Welcom!", "You're welcome! It means a lot."]
            response = {
                "text": random.choice(welcome_texts)
            }
        elif 'nlp' in received_message:
            nlp = received_message['nlp']
            if 'entities' in nlp:
                entities = nlp['entities']
                if ('greetings' in entities) and (entities['greetings'][0]['confidence'] > 0.7):
                    choice_hello = ['Hi!', 'Hello!', 'Hola!', 'Hey!']
                    response_greeting = random.choice(choice_hello)
                    response = {
                        "text": f"{response_greeting} {profile_info['first_name']}."
                    }
                else:
                    exception_texts = [
                        "Sorry, I don't quite understand that!",
                        "I can’t make head nor tail of what you’re saying. Sorry for the inconvenience",
                        "Sorry this is as clear as mud to me.",
                        "Sorry, have no clue of what you are saying.",
                        "It's beyond my understanding what you're saying. I apologize"
                    ]
                    response = {
                        "text": random.choice(exception_texts) 
                    }

                call_send_api(sender_psid, response)
                set_sender_status(sender_psid, 'typing_on')
                response ={
                    "text": "Try one of the options in the menu."
                }
                call_send_api(sender_psid, response)
                set_sender_status(sender_psid, 'typing_on')
                response ={
                    "text": "or Get Updates:",
                    "quick_replies":[
                    {
                        "content_type":"text",
                        "title":"Global Update",
                        "payload":"total_global_cases",
                        "image_url":"https://i.ibb.co/smC141c/earth-PNG5.png"
                    },{
                        "content_type":"text",
                        "title":"Nepal Update",
                        "payload":"total_nepal_cases",
                        "image_url":"https://i.ibb.co/F0Vk56C/flag-of-nepal-national-flag-national-symbols-of-nepal-flag-png-clip-art.png"
                    },
                    {
                        "content_type":"text",
                        "title":"USA",
                        "payload":"usa",
                        "image_url":"https://i.ibb.co/XFJZDjY/78-786836-icon-svg-american-us-flag-image-usa-flag.png"
                    },
                    {
                        "content_type":"text",
                        "title":"Other Countries",
                        "payload":"other_countries",
                        "image_url":"https://i.ibb.co/bP289TY/computer-icons-internet-world-wide-web-clip-art-wh.png"
                    }
                    ]
                }

    elif 'attachments' in received_message:
        attachment_url = received_message['attachments'][0]['payload']['url']
        complementing_words = ['Nice', 'Super','Fantastic', 'HaHaHa','Nice one','Whoa!', 'Good one', 'Noicee', 'Noicee','Noicee', 'Lovely']
        response = {
            "text": random.choice(complementing_words)
        }
        # response = {
        #     "attachment": {
        #         "type": "template",
        #         "payload": {
        #         "template_type": "generic",
        #         "elements": [{
        #             "title": "Is this the right picture?",
        #             "subtitle": "Tap a button to answer.",
        #             "image_url": attachment_url,
        #             "buttons": [
        #             {
        #                 "type": "postback",
        #                 "title": "Yes!",
        #                 "payload": "yes",
        #             },
        #             {
        #                 "type": "postback",
        #                 "title": "No!",
        #                 "payload": "no",
        #             }
        #             ],
        #         }]
        #         }
        #     }
        # }
    call_send_api(sender_psid, response)

def handle_postback(sender_psid, received_message, profile_info):
    # print(received_message)
    payload = received_message['payload']

    # If get started is called
    if(payload == "greeting"):
        response = { 
            "text":  f"Hello! {profile_info['first_name']}, Are you staying at home?",
            "quick_replies":[
            {
                "content_type":"text",
                "title":"Yeah! ",
                "payload":"yeah_staying_home",
                "image_url":"https://smallimg.pngkey.com/png/small/0-4418_image-checkmark-green-circle-check-mark.png"
            },{
                "content_type":"text",
                "title":"Nope! ",
                "payload":"not_staying_home",
                "image_url":"https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Cross_red_circle.svg/600px-Cross_red_circle.svg.png"
            }
            ]
        }   
    # if(payload == 'yes'):
    #     response = { "text": "Thanks!" }
     # elif(payload == 'no'):
    #     response = { "text": "Oops, try sending another image." }
    elif(payload == 'yeah_staying_home'):
        response = { "text": "That's good! You are keeping yourself as well as others safe." }
        call_send_api(sender_psid,response)
        set_sender_status(sender_psid,'typing_on')
        response ={
            "text": "Would you like some updates?",
            "quick_replies":[
            {
                "content_type":"text",
                "title":"Global Update",
                "payload":"total_global_cases",
                "image_url":"https://i.ibb.co/smC141c/earth-PNG5.png"
            },{
                "content_type":"text",
                "title":"Nepal Update",
                "payload":"total_nepal_cases",
                "image_url":"https://i.ibb.co/F0Vk56C/flag-of-nepal-national-flag-national-symbols-of-nepal-flag-png-clip-art.png"
            },
            {
                "content_type":"text",
                "title":"USA",
                "payload":"usa",
                "image_url":"https://i.ibb.co/XFJZDjY/78-786836-icon-svg-american-us-flag-image-usa-flag.png"
            },
            {
                "content_type":"text",
                "title":"Other Countries",
                "payload":"other_countries",
                "image_url":"https://i.ibb.co/bP289TY/computer-icons-internet-world-wide-web-clip-art-wh.png"
            }
            ]
        }
    elif(payload == 'not_staying_home'):
        response = { "text": "Whoa! PLEASE help to flatten the curve by staying home."}
        call_send_api(sender_psid,response)
        set_sender_status(sender_psid,'typing_on')
        response ={
            "text": "Learn More on:",
            "quick_replies":[
            {
                "content_type":"text",
                "title":"Preventive Measures",
                "payload":"preventive_measures",
            },{
                "content_type":"text",
                "title":"Compare with flu",
                "payload":"compare_symptoms_with_flu",
            }
            ]
        }
   
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
        response = get_covid_update('all')
    elif(payload == "total_nepal_cases"):
        response = get_covid_update('nepal')
    elif(payload == "usa"):
        response = get_covid_update('usa')
    elif(payload == 'other_countries'):
        response ={
            "text": "The affected countries/regions are: \n" + '\n'.join(AFFECTED_COUNTRIES).replace('caribbean netherlands','china')[:1916] + "\nTry typing one of the countries."
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
    return response

def get_covid_update(country):
    try:
        response ={
            "attachment":{
            "type":"template",
            "payload":{
                "template_type":"button",
                "text":covid_update(country),
                "buttons":[
                {
                    "type":"web_url",
                    "url":"https://www.worldometers.info/coronavirus/",
                    "title":"Get More Info"
                },
                ]
            }
            }
        }
    except Exception as e:
        print("Exception from api:  ")
        print(e)
        response = {
            "Sorry! We encountered some problem. We'll get back to you soon."
        }
    return response


if __name__ == "__main__":
    app.run('localhost',5000)
        

