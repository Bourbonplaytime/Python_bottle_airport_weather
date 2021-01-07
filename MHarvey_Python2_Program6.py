#Un: Matt Pw: Python or Un: Dayna Pw: Terry

import sqlite3
import hashlib
import uuid
import requests
from bottle import route, run, request, response, redirect, template

@route('/', method='GET')
def index():
    data = {'title': 'Welcome'}
    if not request.get_cookie('user'):
        return template('index', data)
    else:
        return template('airport', data)

@route('/signup', method='POST')
def signup():
    data = {'title': 'Signup'}
    if not request.get_cookie('user'):
        return template('signup', data)
    else:
        redirect('/')

@route('/enter', method='POST')
def enter():
    user = request.forms.get('username')
    pw = request.forms.get('password')

    pw = pw.encode('utf-8')
    pw = hashlib.sha1(pw).hexdigest()

    conn = sqlite3.connect('weather_db.sqlite')
    c = conn.cursor()

    sql = "INSERT INTO login VALUES (NULL, ?, ?)"
    c.execute(sql, (user, pw))

    conn.commit()
    c.close()

    redirect('/')

@route('/login', method='POST')
def login():
    user = request.forms.get('username')
    pw = request.forms.get('password')

    pw = pw.encode('utf-8')
    pw = hashlib.sha1(pw).hexdigest()

    conn = sqlite3.connect('weather_db.sqlite')
    c = conn.cursor()

    sql = "SELECT * FROM login WHERE username = ? and password = ?"
    c.execute(sql, (user, pw))
    result = c.fetchone()

    if result:
        cookie_value = str(uuid.uuid4())
        response.set_cookie('user', cookie_value)
        c.close()
        return template('airport')
    else:
        c.close()
        redirect('/')

@route('/flightdata', method='POST')
def flight_data():
    if not request.get_cookie('user'):
        redirect('/')

    value = request.forms.get('airports')

    response = requests.get('http://api.geonames.org/weatherIcaoJSON?ICAO=' + value + '&username=jctcstudents')
    data = response.json()

    stationName = data['weatherObservation']['stationName']
    elevation = round(data['weatherObservation']['elevation'] * 3.28084, 1)
    dewPoint = round(float(data['weatherObservation']['dewPoint']) * 1.8 + 32)
    clouds = data['weatherObservation']['clouds']
    windSpeed = round(float(data['weatherObservation']['windSpeed']) * 1.15078, 1)
    temperature = round(float(data['weatherObservation']['temperature']) * 1.8 + 32)
    humidity = data['weatherObservation']['humidity']

    final_data = {'stationName': stationName, 'elevation': elevation, 'clouds': clouds, 'dewPoint': dewPoint, 'windSpeed': windSpeed, 'temperature': temperature, 'humidity': humidity}

    return template('airport', final_data)



run(host='localhost', port=8080)
