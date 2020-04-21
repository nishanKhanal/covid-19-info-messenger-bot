import requests, os
from datetime import datetime, timezone as tz
from pytz import timezone

temp = ["USA","Spain","Italy","France","Germany","UK","Turkey","Iran","Russia","Belgium","Brazil","Canada","Netherlands","Switzerland","Portugal","India","Peru","Ireland","Austria","Sweden","Israel","Japan","S. Korea","Saudi Arabia","Chile","Ecuador","Poland","Romania","Pakistan","Mexico","Singapore","Denmark","UAE","Norway","Czechia","Indonesia","Serbia","Australia","Philippines","Qatar","Ukraine","Malaysia","Belarus","Dominican Republic","Panama","Finland","Colombia","Luxembourg","South Africa","Egypt","Morocco","Bangladesh","Argentina","Thailand","Algeria","Moldova","Greece","Kuwait","Hungary","Bahrain","Croatia","Kazakhstan","Iceland","Uzbekistan","Iraq","Estonia","New Zealand","Oman","Azerbaijan","Armenia","Slovenia","Lithuania","Bosnia and Herzegovina","North Macedonia","Slovakia","Ghana","Cuba","Afghanistan","Hong Kong","Cameroon","Bulgaria","Tunisia","Ivory Coast","Djibouti","Cyprus","Latvia","Andorra","Diamond Princess","Lebanon","Costa Rica","Niger","Nigeria","Albania","Guinea","Burkina Faso","Kyrgyzstan","Bolivia","Uruguay","Channel Islands","Honduras","San Marino","Palestine","Malta","Taiwan","Jordan","Réunion","Georgia","Senegal","Mauritius","DRC","Montenegro","Sri Lanka","Isle of Man","Guatemala","Kenya","Mayotte","Vietnam","Venezuela","Mali","El Salvador","Paraguay","Jamaica","Faeroe Islands","Tanzania","Somalia","Martinique","Congo","Guadeloupe","Rwanda","Brunei","Gibraltar","Cambodia","Madagascar","Trinidad and Tobago","Myanmar","Ethiopia","Gabon","Aruba","French Guiana","Monaco","Sudan","Liberia","Bermuda","Togo","Liechtenstein","Equatorial Guinea","Barbados","Sint Maarten","Cabo Verde","Maldives","Guyana","Zambia","Cayman Islands","Bahamas","French Polynesia","Uganda","Benin","Libya","Guinea-Bissau","Haiti","Macao","Sierra Leone","Syria","Eritrea","Mozambique","Saint Martin","Chad","Mongolia","Nepal","Zimbabwe","Angola","Antigua and Barbuda","Eswatini","Timor-Leste","Botswana","Laos","Belize","Fiji","New Caledonia","Malawi","Dominica","Namibia","Saint Kitts and Nevis","Saint Lucia","Curaçao","Grenada","CAR","St. Vincent Grenadines","Turks and Caicos","Falkland Islands","Greenland","Montserrat","Seychelles","Nicaragua","Gambia","Suriname","MS Zaandam","Vatican City","Mauritania","Papua New Guinea","St. Barth","Western Sahara","British Virgin Islands","Burundi","Bhutan","Caribbean Netherlands","Sao Tome and Principe","South Sudan","Anguilla","Saint Pierre Miquelon","Yemen","China"]
AFFECTED_COUNTRIES=[]
for country in temp:
    AFFECTED_COUNTRIES.append(country.lower())

def covid_update(country="all"):
    # use all for world and country name for specific country data

    #header is same for both apis
    headers = {
        'x-rapidapi-host': "coronavirus-monitor.p.rapidapi.com",
        'x-rapidapi-key': os.environ.get('X_RAPIDAPI_KEY')
    }

    api_response = ''
    try:
        if country == "all":        
            url = "https://coronavirus-monitor.p.rapidapi.com/coronavirus/worldstat.php"
            api_response = requests.request("GET", url, headers=headers, timeout=5)
        else:
            url = "https://coronavirus-monitor.p.rapidapi.com/coronavirus/latest_stat_by_country.php"
            querystring = {"country":country}
            api_response = requests.request("GET", url, headers=headers, params=querystring, timeout=5)
        print("First api is running")
        #if this api is working then
        response = api_response.json() if country == 'all' else api_response.json()['latest_stat_by_country'][0]
        data = {}
        data['country_name'] = 'Global' if country == 'all' else response['country_name']
        try:
            data['total_confirmed'] = int(response['total_cases'].replace(',',''))
        except : #both Value error and Type error can occure
            data['total_confirmed'] = 0

        try:
            data['total_deaths'] = int(response['total_deaths'].replace(',',''))
        except :
            data['total_deaths'] = 0
        
        try:
            data['total_recovered'] = int(response['total_recovered'].replace(',',''))
        except :
            data['total_recovered'] = 0

        try:
            data['new_cases'] = int(response['new_cases'].replace(',',''))
        except :
            data['new_cases'] = 0

        try:
            data['new_deaths'] = int(response['new_deaths'].replace(',',''))
        except :
            data['new_deaths'] = 0

        get_unformated_time = response['statistic_taken_at'] if country == 'all' else response['record_date']
        try:
            get_unformated_time = get_unformated_time[:get_unformated_time.index('.')]
        except:
            pass
        last_updated_UTC = datetime.fromisoformat(get_unformated_time.replace(' ','T')+"+00:00")

    except requests.exceptions.Timeout:
        #2nd Api that updates every 15 minutes
        print('second api is running')
        url = "https://covid-193.p.rapidapi.com/statistics"

        querystring = {"country":country}

        api_response = requests.request("GET", url, headers=headers, params=querystring)
        response = api_response.json()['response'][0]
        data = {}
        data['country_name'] = response['country'] if response['country'] not in ['ALL', 'all'] else 'Global'

        try:
            data['total_confirmed'] = int(response['cases']['total'])
        except TypeError:
            data['total_confirmed'] = 0

        try:
            data['total_deaths'] = int(response['deaths']['total'])
        except TypeError:
            data['total_deaths'] = 0
        
        try:
            data['total_recovered'] = int(response['cases']['recovered'])
        except TypeError:
            data['total_recovered'] = 0

        try:
            data['new_cases'] = int(response['cases']['new'])
        except TypeError:
            data['new_cases'] = 0

        try:
            data['new_deaths'] = int(response['deaths']['new'])
        except TypeError:
            data['new_deaths'] = 0

        last_updated_UTC = datetime.fromisoformat(response['time'])


    last_updated_NST = last_updated_UTC.astimezone(timezone('Asia/Kathmandu'))
    current_time_UTC = datetime.now(tz.utc)
    formatted_time = last_updated_NST.strftime('%d %b,%Y %H:%M:%S ')
    delta = current_time_UTC - last_updated_UTC

    if delta.seconds >= 60:
        minutes = delta.seconds // 60
        time_ago = f"{minutes} minutes ago" if minutes>1 else f"{minutes} minute ago"
    else:
        seconds = delta.seconds
        time_ago = f"{seconds} seconds ago" if seconds>1 else f"{seconds} second ago"
    updated_data = f"{data['country_name']} UPDATE:\n\nTOTAL CONFIRMED CASES: {data['total_confirmed']:,}\n\nTOTAL DEATHS: {data['total_deaths']:,}\n\nTOTAL RECOVERED: {data['total_recovered']:,}\n\nNEW CASES: +{data['new_cases']:,}\n\nNEW DEATHS: +{data['new_deaths']:,}\n\nLAST UPDATED: {formatted_time} ({time_ago})"
    return updated_data
