from datetime import datetime, time
from itertools import groupby

import requests
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

app.jinja_env.add_extension('jinja2.ext.do')

client = MongoClient('localhost', 27017)
db = client.metcast

API_KEY = 'cd62149871d972ab50a11189467f1bd6'
FIND_URL = 'http://api.openweathermap.org/data/2.5/find'
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast'

DAYS = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота',
        'Воскресенье')
NOON = time(12, 00)


def normalize_wind_deg(deg):
    towards = (0, 23, 45, 68, 90, 113, 135, 158, 180, 203, 225, 248, 270, 293,
               313, 336)
    for toward in towards:
        if toward - 12 < deg < toward + 12:
            return toward
    return 0


def normalize_icon(own_icon):
    map_ = {'01d': 'wi wi-day-sunny', '01n': 'wi wi-night-clear',
            '02d': 'wi wi-day-cloudy', '02n': 'wi wi-night-alt-cloudy',
            '03d': 'wi wi-cloud', '03n': 'wi wi-cloud',
            '04d': 'wi wi-cloudy', '04n': 'wi wi-cloudy',
            '09d': 'wi wi-rain', '09n': 'wi wi-rain',
            '10d': 'wi wi-day-rain', '10n': 'wi wi-night-alt-hail',
            '11d': 'wi wi-thunderstorm', '11n': 'wi wi-thunderstorm',
            '13d': 'wi wi-snow', '13n': 'wi wi-snow'}
    return map_.get(own_icon, 'wi wi-na')

@app.route('/')
def index():
    params = dict()
    if request.args.get('id'):
        params['id'] = request.args.get('id')
    elif request.args.get('lat') and request.args.get('lon'):
        params['lat'] = request.args.get('lat')
        params['lon'] = request.args.get('lon')
    elif request.args.get('q'):
        params['q'] = request.args.get('q')
    else:
        params['id'] = 701404  # Melitopol

    params['units'] = request.args.get('units', 'metric')
    params['lang'] = request.args.get('lang', 'ru')
    params['APPID'] = API_KEY

    now = datetime.now()
    zero = datetime.fromtimestamp(0)
    for forecast in db.forecast.find(params):
        delta = now - forecast.get('inner_dt', zero)
        if delta.seconds <= 3 * 60 * 60:
            response = forecast
            from_db = True

            print('_______from_db_______')
            print('date:', now)
            print('city:', response['city'])
            print('_____________________')

            break
    else:
        data = requests.get(FORECAST_URL, params=params).json()
        from_db = False

        for forecast in data['list']:
            forecast['dt'] = datetime.fromtimestamp(forecast['dt'])
        response = {'weather': [], 'inner_dt': now}
        response.update(params)

        now_date = datetime.now().date()
        num = 0
        for key, weather in groupby(data['list'], lambda x: (x['dt'].weekday(), x['dt'].day)):
            num += 1
            if num > 5: break

            weekday, day = key
            result = dict()
            result['date'] = '{weekday} {day}'.format(weekday=DAYS[weekday],
                                                      day=day)

            weather_list = list(weather)
            daily_forecast = weather_list[0]
            result['list'] = []
            for forecast in weather_list:
                if forecast['dt'].date() == now_date:
                    daily_forecast = weather_list[0]
                elif forecast['dt'].time() == NOON:
                    daily_forecast = forecast

                normal_icon = normalize_icon(forecast['weather'][0]['icon'])
                forecast['weather'][0]['icon'] = normal_icon
                forecast['time'] = forecast.pop('dt').strftime('%H:%M')
                normal_wind_deg = normalize_wind_deg(forecast['wind']['deg'])
                forecast['wind']['deg'] = normal_wind_deg
                result['list'].append(forecast)

            result['temp'] = daily_forecast['main']['temp']
            result['icon'] = daily_forecast['weather'][0]['icon']
            result['description'] = daily_forecast['weather'][0]['description']

            response['weather'].append(result)

        response['city'] = data['city']

    if not from_db:
        db.forecast.insert_one(response)

    units = 'celsius' if params['units'] == 'metric' else 'fahrenheit'
    return render_template('index.html', data=response, units=units)


@app.route('/find')
def find():
    if not request.args.get('q'):
        return jsonify({'code': 404})
    params = dict()
    params['q'] = request.args.get('q')
    params['units'] = request.args.get('units', 'metric')
    params['lang'] = request.args.get('lang', 'ru')
    params['APPID'] = API_KEY
    return requests.get(FIND_URL, params=params).content


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
