import requests, json

ACCESS_TOKEN ="EAADN3saaUZC8BAHRzadX7ygVr2KerNP4AMn4xDDkA6SEYp2dnD5SwpAszsMWLHA87lK0U3ZBTZCtUczama2JZCTuhw9pAKAZCZCFZCqmYQfAQ4vHqoHYcso5iEFwze8w31ycEmuaC45FuBrJcGVptuYnM4aQqbHC2IX71BuTitVDAZDZD"
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
            "text":"Hello! {{user_first_name}}" 
        }, {
            "locale":"en_US",
            "text":"Timeless apparel for the masses."
        }
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


