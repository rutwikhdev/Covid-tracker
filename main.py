from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        all_data = requests.get('https://api.covid19api.com/summary')
        # saveData(all_data.json(), 'generaldata.json')       # saving the latest data incase api goes down
        ww_stats = all_data.json()['Global']
        countries = all_data.json()['Countries']
    except:
        with open('generaldata.json', 'r') as json_file:
            all_data = json.load(json_file)
            ww_stats = all_data['Global']
            countries = all_data['Countries']

    rp = int((ww_stats['TotalRecovered'] / ww_stats['TotalConfirmed']) * 100)
    dp = int((ww_stats['TotalDeaths'] / ww_stats['TotalConfirmed']) * 100)

    c_cases = {x['Country']: x['TotalConfirmed'] for x in countries}

    top_countries = dict(sorted(c_cases.items(), key=lambda c_cases: c_cases[1], reverse=True))     # sorting based on number of cases
    top_countries = {k: top_countries[k] for k in list(top_countries)[:10]}     # picking only first 10
    params = {
        'ww_total_conf': ww_stats['TotalConfirmed'],
        'ww_total_rec': ww_stats['TotalRecovered'],
        'ww_total_dea': ww_stats['TotalDeaths'],
        'recovery_perc': rp,
        'deaths_perc': dp,
        'tcountries': top_countries
    }

    return render_template('index.html', params=params)


@app.route('/byCountry', methods=['GET', 'POST'])
def byCountry():
    country = request.form['nation']
    country = country[:1].upper() + country[1:]

    try:
        all_data = requests.get('https://api.covid19api.com/country/' + country)
        print(all_data.json())
        # saveData(all_data.json(), 'countrydata.json')
        all_data = all_data.json()
    except:
        with open('countrydata.json','r') as json_file:
            all_data = json.load(json_file)

    confirmed = []
    deaths = []
    recovered = []
    for i, day in enumerate(all_data):
        if day['Confirmed'] == 0 :
            pass
        else:
            if i % 3 == 0:
                confirmed.append({'x': day['Date'][:10], 'y': day['Confirmed']})
                recovered.append({'x': day['Date'][:10], 'y': day['Recovered']})
                deaths.append({'x': day['Date'][:10], 'y': day['Deaths']})

    d = {
        'confirmed': confirmed,
        'recovered': recovered,
        'deaths': deaths
    }

    latest_data = all_data[-1]
    rp = int((latest_data['Recovered']/latest_data['Confirmed'])*100)
    dp = int((latest_data['Deaths']/latest_data['Confirmed'])*100)

    params = {
        'country': country,
        'latest_conf': latest_data['Confirmed'],
        'latest_rec': latest_data['Recovered'],
        'latest_act': latest_data['Active'],
        'latest_dea': latest_data['Deaths'],
        'recovery_perc': rp,
        'deaths_perc': dp
    }

    return render_template('country.html', detailed=json.dumps(d), params=params)


def saveData(dump, file):
    with open(file, 'w') as jsonfile:
        json.dump(dump, jsonfile)

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')
