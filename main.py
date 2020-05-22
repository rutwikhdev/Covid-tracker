from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    all_data = requests.get('https://api.covid19api.com/summary')
    saveData(all_data.json())

    # if the api is taken down or stops responding uncomment the following two lines inorder to use the saved dummy data in .json files
    # with open('generaldata.json', 'r') as json_file:
    #     all_data = json.load(json_file)

    ww_stats = all_data.json()['Global']
    # ww_stats = all_data['Global']
    rp = int((ww_stats['TotalRecovered']/ww_stats['TotalConfirmed'])*100)
    dp = int((ww_stats['TotalDeaths']/ww_stats['TotalConfirmed'])*100)

    countries = all_data.json()['Countries']
    # countries = all_data['Countries']
    c_to_cases = {}
    top_countries_data = []
    for index in range(len(countries)):
        country = countries[index]['Country']
        cases = countries[index]['TotalConfirmed']
        c_to_cases.update({country: cases})
    keys = list(c_to_cases.keys())
    values = list(c_to_cases.values())

    for i in range(20):
        ndx = values.index(max(values))
        key = keys[ndx]
        top_countries_data.append((key, max(values)))
        keys.remove(key)
        values.remove(max(values))

    return render_template('index.html', worldwide=ww_stats, recovery_perc=rp, deaths_perc=dp, tcountries=top_countries_data)


@app.route('/byCountry', methods=['GET', 'POST'])
def byCountry():
    country = request.form['nation']
    country = country[:1].upper()+country[1:]
    all_data = requests.get('https://api.covid19api.com/country/'+country)
    all_data = all_data.json()
    
    # if the api is taken down or stops responding uncomment the following two lines inorder to use the saved dummy data in .json files
    # with open('countrydata.json','r') as json_file:
    # all_data = json.load(json_file)

    latest_data = all_data[-1]
    rperc = int((latest_data['Recovered']/latest_data['Confirmed'])*100)
    dperc = int((latest_data['Deaths']/latest_data['Confirmed'])*100)

    return render_template('country.html', country=country, latest=latest_data, rperc=rperc, dperc=dperc)


def saveData(pointer):
    with open('generaldata.json', 'w') as jsonfile:
        json.dump(pointer, jsonfile)


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')
