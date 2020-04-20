import requests, os
from datetime import datetime, timezone as tz
from pytz import timezone

def covid_update(country="all"):
    # use all for world and country name for specific country data

    #header is same for both apis
    headers = {
        'x-rapidapi-host': "coronavirus-monitor.p.rapidapi.com",
        'x-rapidapi-key': os.environ.get('X_RAPIDAPI_KEY')
    }

    api_response = ''
    if country == "all":        
        url = "https://coronavirus-monitor.p.rapidapi.com/coronavirus/worldstat.php"
        api_response = requests.request("GET", url, headers=headers)
    else:
        url = "https://coronavirus-monitor.p.rapidapi.com/coronavirus/latest_stat_by_country.php"
        querystring = {"country":country}
        api_response = requests.request("GET", url, headers=headers, params=querystring)
  
    if api_response not in ['', ' ']:
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

    else:
    #2nd Api that updates every 15 minutes
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
        time_ago = f"{minutes} minutes ago" if minutes>1 else f"{minutes} minutes ago"
    else:
        seconds = delta.seconds
        time_ago = f"{seconds} seconds ago" if seconds>1 else f"{seconds} second ago"
    updated_data = f"{data['country_name']} UPDATE:\n\nTOTAL CONFIRMED CASES: {data['total_confirmed']:,}\n\nTOTAL DEATHS: {data['total_deaths']:,}\n\nTOTAL RECOVERED: {data['total_recovered']:,}\n\nNEW CASES: +{data['new_cases']:,}\n\nNEW DEATHS: +{data['new_deaths']:,}\n\nLAST UPDATED: {formatted_time} ({time_ago})"
    return updated_data
