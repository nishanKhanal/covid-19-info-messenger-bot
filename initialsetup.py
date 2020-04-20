import requests, json, os
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
URL_MESSENGER_PROFILE = f"https://graph.facebook.com/v2.6/me/messenger_profile?access_token={ACCESS_TOKEN}"

#Includes Get Started
headers = {"Content-Type": "application/json", }
data = {"get_started": {"payload": "greeting"} }
response = requests.post(URL_MESSENGER_PROFILE, headers=headers, data=json.dumps(data))

# Greeting
data = {
    "greeting": [
        {
            "locale":"default",
            "text":"Hello! {{user_first_name}}. This bot provides information on coronavirus. Get started to learn more about the disease. \n Compare this disease with seasonal flu and common cold. It uses the CDC, WHO and public data by Johns Hopkins CSSE as source of data and information" 
        }, 
    ]
}
response = requests.post(URL_MESSENGER_PROFILE, headers=headers, data=json.dumps(data))

#Adds Persistent Menu
data = {
        "persistent_menu":[
        {
            "locale":"default",
            "composer_input_disabled": False,
            "call_to_actions":[
            {
                "title":"Covid Info",
                "type":"nested",
                "call_to_actions":[
                {
                    "title":"About Covid-19",
                    "type":"postback",
                    "payload":"about_covid_19"
                },
                {
                    "title":"Symptoms",
                    "type":"postback",
                    "payload":"symptoms"
                },
                {
                    "title":"Preventive Measures",
                    "type":"postback",
                    "payload":"preventive_measures"
                }
                ]
            },
            {
                "title":"LATEST UPDATES",
                "type":"nested",
                "call_to_actions":[
                {
                    "title":"Global Update",
                    "type":"postback",
                    "payload":"total_global_cases"
                },
                {
                    "title":"Nepal Update",
                    "type":"postback",
                    "payload":"total_nepal_cases"
                },
                {
                    "title":"Other Countries",
                    "type":"postback",
                    "payload":"other_countries"
                }
                ]
            },
            {
                "title":"Compare with Flu",
                "type":"nested",
                "call_to_actions":[
                {
                    "title":"Compare Symptoms with flu",
                    "type":"postback",
                    "payload":"compare_symptoms_with_flu"
                },
                {
                    "title":"Compare Stat with flu",
                    "type":"postback",
                    "payload":"compare_stat_with_flu"
                }
                ]
            },
            # {
            #     "type":"postback",
            #     "title":"Latest Posts",
            #     "payload":"LATEST_POST_PAYLOAD"
            # },
            ]
        }
        ]
    }

response = requests.post(URL_MESSENGER_PROFILE, headers=headers, data=json.dumps(data))
print(response.text)